import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatMessage, Reg
from profanity_check import predict

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = "global_chat"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"WebSocket CONNECTED: {self.channel_name}")

        # Send existing messages to the newly connected client
        await self.send_existing_messages()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"WebSocket DISCONNECTED: {self.channel_name}")

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            print("Received WebSocket data:", text_data_json)

            sender_id = text_data_json.get("sender_id")
            action = text_data_json.get("action", "send_message")

            if not sender_id:
                await self.send(text_data=json.dumps({"error": "Missing sender_id"}))
                return

            if action == "send_message":
                message = text_data_json.get("message", "")
                if message:
                    # Check for profanity
                    is_profane = predict([message])[0]  # Returns 1 if profane, 0 if not
                    if is_profane == 1:
                        await self.send(text_data=json.dumps({"error": "Message contains inappropriate content"}))
                        return  # Prevent saving or broadcasting the message

                    # If no profanity, proceed to save and broadcast
                    message_obj = await self.save_message(sender_id, message)
                    sender_name = await self.get_sender_name(sender_id)
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "message": message,
                            "sender_id": sender_id,
                            "sender_name": sender_name,
                            "messageId": str(message_obj.id),
                            "timestamp": message_obj.timestamp.isoformat(),
                        }
                    )

            elif action == "delete":
                message_id = text_data_json.get("messageId")
                if message_id:
                    success = await self.delete_message(message_id, sender_id)
                    print(f"Message deletion success: {success} for message_id: {message_id}")
                    if success:
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {"type": "chat_delete", "messageId": message_id}
                        )
                    else:
                        await self.send(text_data=json.dumps({"error": "You can only delete your own messages"}))

        except json.JSONDecodeError:
            print("Invalid JSON data received")
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))

    async def chat_message(self, event):
        """Broadcasts chat messages to the client"""
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "sender_id": event["sender_id"],
            "sender_name": event["sender_name"],
            "messageId": event["messageId"],
            "timestamp": event["timestamp"],
        }))

    async def chat_delete(self, event):
        """Handles message deletion"""
        await self.send(text_data=json.dumps({
            "action": "delete",
            "messageId": event["messageId"],
        }))

    @database_sync_to_async
    def save_message(self, sender_id, message):
        """Saves chat messages in the database"""
        sender = Reg.objects.get(id=sender_id)
        return ChatMessage.objects.create(sender=sender, message=message, is_read=False)

    @database_sync_to_async
    def get_sender_name(self, sender_id):
        """Fetches the sender's name"""
        sender = Reg.objects.get(id=sender_id)
        return sender.name

    @database_sync_to_async
    def delete_message(self, message_id, sender_id):
        """Deletes a chat message if it belongs to the sender"""
        try:
            message = ChatMessage.objects.get(id=message_id)
            print(f"Attempting to delete message: {message} by sender_id: {sender_id}")
            if str(message.sender.id) == str(sender_id):
                message.delete()
                return True
            return False
        except ChatMessage.DoesNotExist:
            return False

    @database_sync_to_async
    def get_existing_messages(self):
        """Fetches all existing messages from the database"""
        messages = ChatMessage.objects.all().order_by("timestamp")
        return [
            {
                "message": msg.message,
                "sender_id": str(msg.sender.id),
                "sender_name": msg.sender.name,
                "messageId": str(msg.id),
                "timestamp": msg.timestamp.isoformat(),
            }
            for msg in messages
        ]

    async def send_existing_messages(self):
        """Sends all existing messages to the connected client"""
        messages = await self.get_existing_messages()
        if messages:
            await self.send(text_data=json.dumps({
                "action": "load_messages",
                "messages": messages
            }))