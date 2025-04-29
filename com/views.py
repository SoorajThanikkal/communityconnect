from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .models import *
from django.http import JsonResponse
from groq import Groq
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import logging
from django.core.files.storage import default_storage
from django.conf import settings
import os
import random
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.db.models import Avg
from django.utils.timezone import make_aware
from django.db.models import Avg


def index(request):
    return render(request, 'index.html')
def register(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        passw = request.POST['password']
        confpassw = request.POST['confirm_password']
        contact = request.POST['contact']
        age = request.POST['age']
        location = request.POST['location']
        image = request.FILES.get('img')
        gender = request.POST['gdr']
        bloodgroup = request.POST['bloodgroup']

        # Contact number validation
        if len(contact) != 10 or not contact.isdigit():
            alert = "<script>alert('Contact number must be exactly 10 digits'); window.location.href='/register/';</script>"
            return HttpResponse(alert)

        # Check if user already exists
        if models.Reg.objects.filter(email=email).exists():
            alert = "<script> alert('User already exists'); window.location.href='/register/';</script>"
            return HttpResponse(alert)

        # Password validation
        if len(passw) < 6:
            alert = "<script>alert('Password must be at least 6 characters long'); window.location.href='/register/';</script>"
            return HttpResponse(alert)
        
        if not any(char.isdigit() for char in passw):
            alert = "<script>alert('Password must contain at least one number'); window.location.href='/register/';</script>"
            return HttpResponse(alert)
        
        if not any(char in '@#$%^&+=!' for char in passw):
            alert = "<script>alert('Password must contain at least one special character (@, #, $, etc.)'); window.location.href='/register/';</script>"
            return HttpResponse(alert)

        # Password confirmation
        if passw != confpassw:
            alert = "<script> alert('Passwords do not match');window.location.href='/register/';</script>"
            return HttpResponse(alert)

        # Handle image upload
        image_path = None
        if image:
            image_path = f'profile_images/{image.name}'
            full_path = os.path.join(settings.MEDIA_ROOT, image_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)
        
        # Generate and send OTP
        otp = random.randint(100000, 999999)

        send_mail(
            "Your OTP for Registration",
            f"Hello {name},\n\nYour OTP for registration is: {otp}\n\nPlease enter this OTP to verify your email.",
            "your_email@example.com",
            [email],
            fail_silently=False,
        )

        # Store data in session
        request.session['registration_data'] = {
            'name': name, 'email': email, 'passw': passw,
            'contact': contact, 'age': age, 'location': location,
            'img': image_path, 'gender': gender, 'bloodgroup': bloodgroup,
            'otp': str(otp)
        }
        return redirect('otp')

    return render(request, 'register.html')


def otp(request):
    if request.method == 'POST':
        entered_otp = request.POST['otp']
        session_data = request.session.get('registration_data')

        if session_data and session_data['otp'] == entered_otp:
            # Save the user in the database
            user = models.Reg.objects.create(
                name=session_data['name'],
                email=session_data['email'],
                passw=session_data['passw'],
                age=session_data['age'],
                contact=session_data['contact'],
                gender=session_data['gender'],
                image=session_data['img'],
                location=session_data['location'],
                bloodgroup=session_data['bloodgroup']
            )
            user.save()
            del request.session['registration_data']  # Remove session data after success
            return redirect('login')  # Redirect to login page
        else:
            alert = "<script> alert('Invalid OTP');window.location.href='/otp/';</script>"
            return HttpResponse(alert)

    return render(request,'otp.html')


from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from com import models  # Ensure this matches your project structure

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Using .get() to avoid KeyError
        passw = request.POST.get('password')

        user = models.Reg.objects.filter(email=email, passw=passw).first()  # Prevents DoesNotExist error

        if user:
            # Debugging step: Check if user exists
            print(f"User found: {user.name}, Redirecting to userhome...")  

            request.session['email'] = email
            request.session['user_id'] = user.id  # Store user ID in session
            request.session['user_name'] = user.name  # Assuming 'name' field exists
            return redirect('userhome')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('login')  # Redirects with an error message
    return render(request, 'login.html')


def userhome(request):
    if 'email' in request.session:
        email = request.session.get('email')
        user_name = request.session.get('user_name', 'User')
        
        user = models.Reg.objects.filter(email=email).first()
        if user:
            requests = models.Request.objects.all()
            accepted_requests = models.Accept_Request.objects.filter(user=user).values_list('request_id', flat=True)

            return render(request, 'userhome.html', {
                'user_name': user_name,
                'requests': requests,
                'accepted_requests': accepted_requests
            })
    
    return HttpResponse("<script>alert('Something went wrong'); window.location.href='/login/';</script>")

    

def profile(request):
    if 'email' in request.session:
        email=request.session['email']
        user=models.Reg.objects.get(email=email)
        if user:
            return render(request,'profile.html',{'user':user})
        
    alert="<script> alert('something went wrong');window.location.href='/login/';</script>"
    return HttpResponse(alert)
    
from django.shortcuts import render, redirect
from django.http import HttpResponse
from . import models

def delete_useracc(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            user = models.Reg.objects.get(email=email)
            user.delete()  # Delete user from the database
            del request.session['email']  # Remove session data
            return redirect('/')  # Redirect to the register page after deletion
        except models.Reg.DoesNotExist:
            return HttpResponse("<script>alert('User not found!');window.location.href='/profile/';</script>")

    return HttpResponse("<script>alert('Something went wrong!');window.location.href='/login/';</script>")
   
    

def edit_profile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            user = models.Reg.objects.get(email=email)
        except models.Reg.DoesNotExist:
            return redirect('login')  # Redirect if user doesn't exist

        if request.method == 'POST':  # This block was incorrectly indented
            user.name = request.POST.get('name', user.name) or "Default Name"
            user.contact = request.POST.get('contact', user.contact)
            user.gender = request.POST.get('gender', user.gender)
            user.location = request.POST.get('location', user.location)
            user.bloodgroup = request.POST.get('bloodgroup', user.bloodgroup)

            # Convert age safely
            age_value = request.POST.get('age')
            if age_value:
                try:
                    user.age = int(age_value)
                except ValueError:
                    print("Invalid age format")  # Debugging

            # Handle file upload
            if 'image' in request.FILES:
                user.image = request.FILES['image']

            # Save changes
            user.save()
            return redirect('profile')

        return render(request, 'edit_profile.html', {'user': user})

    return redirect('login')



def about(request):
    return render(request,'about.html')

client = Groq(
    api_key="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"  # Directly use the API key
)

# Set up logging to capture request details
logger = logging.getLogger(__name__)

@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        # Log the incoming request data for debugging
        logger.info(f"Received POST request: {request.POST}")
       
        user_message = request.POST.get('message')

        # Check if the message is empty
        if not user_message:
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Modify the message depending on the user's input (for example, checking if it's related to real estate)
        prompt = """
        You are a chatbot designed to assist users of the Community Connect platform. 
        You are the official AI assistant of the CommunityConnect platform—an AI-powered community where socially and mentally well individuals come together to help each other based on their skills, interests, and mindset. Your purpose is to support users in exploring opportunities, connecting with like-minded people, and making the most of their experience on the platform.

Your responsibilities include:

🔹 **Platform Guidance**  
- Guide users in exploring core features: skill-sharing, mentorship, support sessions, volunteering, content creation, and community-driven initiatives.  
- Help with account setup, login issues, and navigating dashboards, profiles, and settings.

🔹 **Mentorship & Support Sessions**  
- Assist users and moderators with session-related actions such as creating, scheduling, joining, or approving sessions.  
- Explain session status (requested, approved, rejected), how links become accessible, and how mentees or mentors can interact.

🔹 **Moderator Assistance**  
- Support moderators in managing community tasks: posting or assigning work, reviewing requests, mentoring users, and offering support.  
- Explain the approval and rejection process, and how moderators contribute to community wellness.

🔹 **Content Creators & Sharing**  
- Help users publish papers, journals, videos, blogs, or creative content related to mental health, personal growth, and social good.  
- Guide them on content filters, reacting or liking posts, and discovering shared contributions.

🔹 **ML/NLP Powered Features**  
- Offer smart matching based on user interests, mindset, and skill sets.  
- Assist in sentiment analysis for content moderation and personalized community suggestions.

🔹 **Volunteering & Blood Donation**  
- Provide steps to request blood, check eligibility, and volunteer as a donor.  
- Explain how donation posts work and how users can respond to urgent needs.

🔹 **Safety, Mental Wellness & Community Support**  
- Promote respectful communication and inclusivity.  
- Offer wellness tips, mental health resources, and encourage positive engagement across the platform.

🔹 **General Help & Troubleshooting**  
- Answer FAQs, help users recover passwords, resolve technical issues, and understand the platform’s flow.  
- Provide actionable tips to maximize user experience and connect meaningfully with the community.

Respectful Communication Reminder
Remind users to avoid using inappropriate language, offensive terms, or any form of harassment.

Encourage a safe and inclusive space by promoting respectful and kind communication across all interactions.

✅ **Your Tone**: Always supportive, concise, and action-oriented. Keep responses clear, helpful, and easy to follow. Use 1–2 sentences unless the question clearly needs a detailed explanation.

Avoid long paragraphs unless the user is asking for in-depth guidance.

Encourage positive interaction and empower users with guidance tailored to their role (user, mentor, moderator, creator, or volunteer).

Remind users to avoid inappropriate language or offensive terms. Promote respectful communication and help maintain a safe, inclusive community for all.
        
        """ 
        # Construct the message for the API
        user_input_message = f"User: {user_message}"

        # Make a request to the Groq API using the SDK
        try:
            chat_completion = client.chat.completions.create(
                messages=[{
                    "role": "user",
                    "content": f"{prompt} {user_input_message}",
                }],
                model="llama-3.3-70b-versatile",  # Specify the model to use
            )

            # Extract the chatbot's reply from the response
            chatbot_reply = chat_completion.choices[0].message.content

            return JsonResponse({'response': chatbot_reply})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return render(request, 'chatbot.html')

def logout(request):
    request.session.flush()
    return redirect('/')  

from django.core.mail import send_mail
from django.conf import settings

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        if not name or not email or not message:
            return render(request, "contact.html", {"error": "All fields are required!"})

        subject = f"Contact Us Message from {name}"
        body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

        try:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,  # Your "from" email
                [email], 
               fail_silently=False, # Admin email to receive messages
            )
            return render(request, "contact.html", {"success": True})
        except Exception as e:
            return render(request, "contact.html", {"error": str(e)})

    return render(request, "contact.html")


from django.shortcuts import render, redirect
from django.contrib import messages
from . import models  # Adjust import if needed

import re  # At the top of your file

def is_strong_password(password):
    return (
        len(password) >= 6 and
        re.search(r'\d', password) and            # At least one number
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)  # At least one special character
    )

def moderator(request):
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        passw = request.POST.get('password')
        confpassw = request.POST.get('confirm_password')
        contact = request.POST.get('contact')
        category = request.POST.get('category')
        img = request.FILES.get('img')
        gender = request.POST.get('gdr')
        bloodgroup = request.POST.get('bloodgroup')

        # Check if user already exists
        if models.Mod.objects.filter(email=email).exists():
            messages.error(request, 'User already exists.')
            return redirect('modregister')

        # Check if passwords match
        if passw != confpassw:
            messages.error(request, 'Passwords do not match.')
            return redirect('modregister')

        # Check password strength
        if not is_strong_password(passw):
            messages.error(request, 'Password is too weak. It must be at least 6 characters long and include a number and a special character.')
            return redirect('modregister')

        try:
            user = models.Mod.objects.create(
                name=name,
                email=email,
                passw=passw,  # plain text password (as you said)
                category=category,
                contact=contact,
                image=img,
                gender=gender,
                bloodgroup=bloodgroup
            )
            user.save()

            return redirect('modlogin')

        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('modregister')

    return render(request, 'modregister.html')
   
    
def modlogin(request):
    if request.method == 'POST':
        email = request.POST['email']
        passw = request.POST['password']
        md = models.Mod.objects.filter(email=email).first()

        if md and md.passw == passw:  # Consider using hashed passwords
            if md.approval_status == 1:
                request.session['email'] = md.email
                print(email)
                request.session['mod_name'] = md.name
                request.session['category'] = md.category  # Store category in session

                # Redirect based on category
                # if md.category == "organizers and facilitators":
                    # return redirect('organizers')
                if md.category == "mentors and experts":
                    return redirect('mentors')
                elif md.category == "sponsors or donors":
                    return redirect('sponsors')
                elif md.category == "creators and sharers":
                    return redirect('creators')
                else:
                    return redirect('mod register')  # Default moderator homepage
            else:
                alert = "<script> alert('Pending for Approval');window.location.href='/modlogin/';</script>"
                return HttpResponse(alert)               
        else:
            alert = "<script> alert('Invalid email or password');window.location.href='/modlogin/';</script>"
            return HttpResponse(alert)
    else:
        return render(request, 'modlogin.html')

#This code is for admin to approve Moderators:-----------------------------------------------------------------------------------------
def mod_approve(request, pk):
    mod = get_object_or_404(models.Mod, id=pk)
    mod.approval_status = True
    mod.save()
    alert="<script> alert('approved successfully');window.location.href='/mod_list/';</script>"
    return HttpResponse(alert)
#to reject moderators
def mod_reject(request, pk):
    mod = get_object_or_404(models.Mod, id=pk)
    mod.delete()
    alert = "<script> alert('Rejected successfully');window.location.href='/mod_list/';</script>"
    return HttpResponse(alert)




#for admin to view all unapproved moderators
def mod_list(request):
    mods = models.Mod.objects.filter(approval_status=False)
    return render(request, 'mod_approve.html', {'mods': mods})

def adminlogin(request):
    if request.method == 'POST':
        email = request.POST.get('email')  
        password = request.POST.get('password')  

        # Hardcoded credentials (not recommended for production)
        ajmal_email = "ajmal@gmail.com"
        ajmal_password = "...."
       
        
        if email == ajmal_email and password == ajmal_password:
            # Redirect to admin home if credentials are correct
            request.session['email']=ajmal_email
            
            return redirect('/adminhome/')
        else:
            ajmal1="<script>alert('Invaild Email or Password - Ajmal');window.location.href='/adminlogin/';</script>"
            return HttpResponse(ajmal1)
        
    return render(request,'adminlogin.html')

def adminhome(request):
    if 'email' in request.session:
        email=request.session['email']
    
        user=models.Reg.objects.count()
        mod=models.Mod.objects.filter(approval_status=True).count()
        uspen=models.Mod.objects.filter(approval_status=0).count()
        pending_moderators = models.Mod.objects.filter(approval_status=False).count()
        requests = models.Request.objects.all().order_by('-uploaded_at')[:5]
        sessions= models.Session_by_Mentor.objects.filter().order_by('-created_at')[:5]
        contents = CreativeContent.objects.filter(moderator=mod).order_by('-created_at')[:5]
        
        
        
    
        context={
             'user':user,
             'mod': mod,
             'uspen':uspen,
             'requests': requests,
             'pending_moderators':pending_moderators,
             'sessions':sessions,
             'contents':contents
        }
     
        return render(request,'adminhome.html', context)
    return redirect('adminlogin')


def modprofile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            user = models.Mod.objects.get(email=email)
            
            # Define category role descriptions
            category_roles = {
                
                "mentors and experts": "Guides users by providing mentorship, career advice, and expertise in specific domains.",
                "sponsors or donors": "Supports the community by taking initiatives or volunteering as blood donors.",
                "creators and sharers": "Creates and shares valuable content such as articles, videos, and educational resources.",
                
            }
            
            role_description = category_roles.get(user.category, "No role assigned.")

            return render(request, 'modprofile.html', {
                'user': user,
                'role_description': role_description
            })

        except models.Mod.DoesNotExist:
            alert = "<script> alert('User not found'); window.location.href='/modlogin/';</script>"
            return HttpResponse(alert)

    alert = "<script> alert('Session expired, please log in again'); window.location.href='/modlogin/';</script>"
    return HttpResponse(alert)

def edit_modprofile(request):
    if 'email' in request.session:
        email = request.session['email']
        try:
            user = models.Mod.objects.get(email=email)
        except models.Mod.DoesNotExist:
            return redirect('modlogin')  # Redirect to login if the user doesn't exist
        
        if request.method == 'POST':
            # Safely retrieve values from POST data and provide defaults if necessary
            user.name = request.POST.get('Name', user.name) or "Default Name"  # Provide a fallback name
            user.email = request.POST.get('Email', user.email) # Retain existing value if not provided
            user.contact = request.POST. get('Phone Number', user.contact)  # Optional field
            user.gender = request.POST.get('gender', user.gender)
            user.bloodgroup = request.POST.get('bloodgroup', user.bloodgroup)
            
            if 'image' in request.FILES:
                user.image = request.FILES.get('image',user.image)    
               
                
            user.save()
            return redirect('modprofile')
        else:
            return render(request, 'edit_modprofile.html', {'user': user})
    else:
        return redirect('modlogin')
    

def userlist(request):
    users=models.Reg.objects.all()
    return render(request,'userlist.html',{'usr':users})

def delete_user(request, user_id):
    user = models.Reg.objects.get(id=user_id)
    user.delete()
    return redirect('userlist')  # Redirect back to the user list page

def moderatorlist(request):
    mods=models.Mod.objects.all()
    return render(request,'moderatorlist.html',{'mod':mods})

def delete_mods(request, user_id):
    mods= models.Mod.objects.get(id=user_id)
    mods.delete()
    return redirect('moderatorlist')

 
def mentors(request):
    if 'email' not in request.session: 
        return redirect('modlogin')

    # Count moderators who are mentors and experts
    active_mentees = Mod.objects.filter(
        category='mentors and experts',
        approval_status=True
    ).count()

    # Count of support sessions completed
    support_sessions_completed = Session_by_Mentor.objects.filter(
        date_time__lt=timezone.now()
    ).count()
    feedback= Feedback.objects.filter(choice='mentors and experts').order_by('-created_at')[:5]
    average_rating = Feedback.objects.filter(choice='mentors and experts').aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating is not None else "N/A"
    
    
    return render(request, 'mentors.html', {
        'active_mentees': active_mentees,
        'support_sessions_completed': support_sessions_completed,
        'average_rating': average_rating,
        'feedback' : feedback
    })


def sponsors(request):
    if 'email' not in request.session: 
        return redirect('modlogin')
    try:
        email= request.session['email']
        mode= Mod.objects.get(email=email)
    except:
        return redirect('modlogin')

    obj = models.AdminRequest.objects.all()

    # Count total approved donors
    total_donors = Mod.objects.filter(
        category='sponsors or donors',
        approval_status=True
    ).count()

    # ✅ Count of all completed donation requests by any sponsor
    donations_collected = Request.objects.filter(status='COMPLETED').count()
    print('ff',mode)
    completed_donations = Request.objects.filter(mod=mode,status='COMPLETED').count()
    feedback= Feedback.objects.filter(choice='sponsors or donors').order_by('-created_at')[:5]
    average_rating = Feedback.objects.filter(choice='sponsors or donors').aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating is not None else "N/A"
    
    print('dd',completed_donations)
    
    return render(request, 'sponsors.html', {
        'obj': obj,
        'total_donors': total_donors,
        'donations_collected': donations_collected,
        'completed_donations': completed_donations,
        'feedback': feedback,
        'average_rating' : average_rating
    })




from django.shortcuts import render, redirect
from django.db.models import Avg
from .models import Mod, CreativeContent, Feedback

def creators(request):
    if 'email' not in request.session: 
        return redirect('modlogin')

    # Count of active creators
    active_creators = Mod.objects.filter(
        category='creators and sharers',
        approval_status=True
    ).count()

    # Group 1: Videos and Files
    video_file_count = CreativeContent.objects.filter(
        content_type__in=['video', 'file', 'other']
    ).count()

    # Group 2: Thoughts, Research, and Articles
    text_based_count = CreativeContent.objects.filter(
        content_type__in=['thought', 'research', 'article']
    ).count()

    # Recent feedback
    feedback = Feedback.objects.filter(choice='creators and sharers').order_by('-created_at')[:5]

    # Average rating rounded to 1 decimal place
    average_rating = Feedback.objects.filter(choice='creators and sharers').aggregate(Avg('rating'))['rating__avg']
    average_rating = round(average_rating, 1) if average_rating is not None else "N/A"

    return render(request, 'creators.html', {
        'active_creators': active_creators,
        'video_file_count': video_file_count,
        'text_based_count': text_based_count,
        'feedback': feedback,
        'feedbackc': average_rating
    })
    

BLOOD_COMPATIBILITY = {
    'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
    'O+': ['O+', 'A+', 'B+', 'AB+'],
    'A-': ['A-', 'A+', 'AB-', 'AB+'],
    'A+': ['A+', 'AB+'],
    'B-': ['B-', 'B+', 'AB-', 'AB+'],
    'B+': ['B+', 'AB+'],
    'AB-': ['AB-', 'AB+'],
    'AB+': ['AB+'],  # Universal recipient, can only donate to AB+
}

def upload_request(request):
    email = request.session.get('email')

    if not email:
        return HttpResponse('Unauthorized: No email found in session')

    try:
        user = Mod.objects.get(email=email)
    except Mod.DoesNotExist:
        return HttpResponse('Error: User not found')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('update_status')
        location = request.POST.get('location')
        bloodgroup = request.POST.get('bloodgroup')  # Blood group needed
        deadline_str = request.POST.get("deadline")
       

        # Convert deadline string to timezone-aware datetime
        if deadline_str:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%dT%H:%M")
            deadline = make_aware(deadline)
        else:
            return HttpResponse('Error: Missing deadline')

        if not title or not description:
            return HttpResponse('Error: Missing title or description')

        # Create new request
        new_request = Request.objects.create(
            mod=user,
            title=title,
            description=description,
            status=status,
            deadline=deadline,
            location=location,
            bloodgroup=bloodgroup
        )
        new_request.save()

        # Get compatible donors
        eligible_blood_groups = BLOOD_COMPATIBILITY.get(bloodgroup, [])
        eligible_donors = Reg.objects.filter(bloodgroup__in=eligible_blood_groups)

        recipient_emails = [donor.email for donor in eligible_donors]
        print(recipient_emails)

        # Send email to compatible donors
        if recipient_emails:
            subject = "Urgent Blood Donation Request"
            message = f"""
            Dear Donor,

            A blood donation request has been made for {bloodgroup} at {location}.
            You are eligible to donate based on your blood type.

            Request Details:
            - Title: {title}
            - Description: {description}
            - Deadline: {deadline.strftime('%Y-%m-%d %H:%M')}

            If you are willing to donate, please contact the organizers.

            Thank you for your support!
            """
            from_email = settings.EMAIL_HOST_USER  # Replace with your sender email
            send_mail(subject, message, from_email, recipient_emails, fail_silently=False)

        category_urls = {
            'mentors and experts': 'mentors',
            'sponsors or donors': 'sponsors',
            'creators and sharers': 'creators',
        }
        dashboard_url = category_urls.get(user.category.lower(), 'home')

        return redirect(dashboard_url)

    return render(request, 'upload_request.html')


def request_list(request):
    requests = Request.objects.all()
    return render(request, "request_list.html", {"requests": requests})

def delete_request(request, request_id):
    request_obj = get_object_or_404(Request, id=request_id)  # Avoid error if ID doesn't exist
    request_obj.delete()
    return redirect('viewrequests') 

def addelete_request(request, request_id):
    request_obj = get_object_or_404(Request, id=request_id)  # Avoid error if ID doesn't exist
    request_obj.delete()
    return redirect('request_list') 
   

def viewrequests(request):
    email = request.session.get('email')
    if email:
        try:
            mod = Mod.objects.get(email=email)
            requests = Request.objects.filter(mod=mod)

            # Count only the completed ones
            

            return render(request, 'viewrequests.html', {
                'requests': requests,
                
            })
        except Mod.DoesNotExist:
            request.session.flush()
            return redirect('modlogin')
    else:
        return redirect('modlogin')

    
    
from django.utils.timezone import now   
def delete_expired_request(request, request_id):
    if request.method == "POST":
        request_obj = get_object_or_404(Request, id=request_id)
        
        # Check if the deadline has passed
        if request_obj.deadline < now():
            request_obj.delete()
            return JsonResponse({"success": True})

    return JsonResponse({"success": False})
    
    
import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib import messages
  # Import user model

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = Reg.objects.filter(email=email).first()

        if user:
            otp = random.randint(100000, 999999)  # Generate 6-digit OTP
            request.session["otp"] = str(otp)  # Store OTP in session
            request.session["email"] = email  # Store email for verification
            request.session["otp_time"] = str(datetime.now())  # Store OTP generation time

            # Send OTP via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                "noreply@yourdomain.com",
                [email],
                fail_silently=False,
            )

            messages.success(request, "If your email is registered, an OTP has been sent.")
            return redirect("verify_otp1")  # Redirect to OTP verification page
        else:
            messages.success(request, "If your email is registered, an OTP has been sent.")

    return render(request, "forgot_password.html")


def verify_otp1(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")  # Get OTP from session
        email = request.session.get("email")  # Get stored email
        otp_time_str = request.session.get("otp_time")

        if not stored_otp or not otp_time_str:
            messages.error(request, "Session expired. Request a new OTP.")
            return redirect("forgot_password")

        otp_time = datetime.strptime(otp_time_str, "%Y-%m-%d %H:%M:%S.%f")

        if datetime.now() > otp_time + timedelta(minutes=5):
            messages.error(request, "OTP has expired. Request a new one.")
            return redirect("forgot_password")

        if entered_otp == stored_otp:
            request.session.pop("otp")  # Remove OTP after successful verification
            return redirect("reset_password")
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, "verify_otp1.html")


from django.contrib import messages
from django.shortcuts import render, redirect
from com.models import Reg  # Replace `yourapp` with your actual app name

def reset_password(request):
    if request.method == "POST":
        email = request.session.get("email")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not email:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect("forgot_password")

        # Password validation
        if len(new_password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, "reset_password.html")
        
        if not any(char.isdigit() for char in new_password):
            messages.error(request, "Password must contain at least one number.")
            return render(request, "reset_password.html")
        
        if not any(char in '@#$%^&+=!' for char in new_password):
            messages.error(request, "Password must contain at least one special character (@, #, $, etc.).")
            return render(request, "reset_password.html")

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "reset_password.html")

        user = Reg.objects.filter(email=email).first()

        if user:
            # Save password as it is (NOT recommended for production)
            user.passw = new_password
            user.save()
            messages.success(request, "Password updated successfully! Please login.")
            return redirect("login")
        else:
            messages.error(request, "User not found.")

    return render(request, "reset_password.html")


def forgot_password2(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = Mod.objects.filter(email=email).first()

        if user:
            otp = random.randint(100000, 999999)  # Generate 6-digit OTP
            request.session["otp"] = str(otp)  # Store OTP in session
            request.session["email"] = email  # Store email for verification
            request.session["otp_time"] = str(datetime.now())  # Store OTP generation time

            # Send OTP via email
            send_mail(
                "Password Reset OTP",
                f"Your OTP for password reset is: {otp}",
                "noreply@yourdomain.com",
                [email],
                fail_silently=False,
            )

            messages.success(request, "If your email is registered, an OTP has been sent.")
            return redirect("verify_otp2")  # Redirect to OTP verification page
        else:
            messages.success(request, "If your email is registered, an OTP has been sent.")

    return render(request, "forgot_password2.html")

def verify_otp2(request):
    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = request.session.get("otp")  # Get OTP from session
        email = request.session.get("email")  # Get stored email
        otp_time_str = request.session.get("otp_time")

        if not stored_otp or not otp_time_str:
            messages.error(request, "Session expired. Request a new OTP.")
            return redirect("forgot_password2")

        otp_time = datetime.strptime(otp_time_str, "%Y-%m-%d %H:%M:%S.%f")

        if datetime.now() > otp_time + timedelta(minutes=5):
            messages.error(request, "OTP has expired. Request a new one.")
            return redirect("forgot_password2")

        if entered_otp == stored_otp:
            request.session.pop("otp")  # Remove OTP after successful verification
            return redirect("reset_password2")
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, "verify_otp2.html")


def reset_password2(request):
    if request.method == "POST":
        email = request.session.get("email")  # Get email from session
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if not email:
            messages.error(request, "Session expired. Please request OTP again.")
            return redirect("forgot_password")

        user = Mod.objects.filter(email=email).first()

        if user:
            if new_password == confirm_password:
                user.passw = new_password  # Store password as plain text (Not Secure)
                user.save()
                messages.success(request, "Password updated successfully! Please login.")
                return redirect("modlogin")
            else:
                messages.error(request, "Passwords do not match.")
        else:
            messages.error(request, "User not found.")

    return render(request, "reset_password2.html")


def accept_request(request, request_id):
    request_data = get_object_or_404(Request, id=request_id)
    return render(request, 'accept_request.html', {'request_data': request_data})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse


def accept(request, request_id):
    accepted_request = get_object_or_404(Request, id=request_id)
    return render(request, "accept.html", {"request_data": accepted_request})

from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

def proceed(request, request_id):
    semail=request.session.get('email')
    user=Reg.objects.get(email=semail)
    request_obj = get_object_or_404(Request, id=request_id)
    
    # request_obj.status = 'completed'
    # request_obj.save()

    moderator_email = request_obj.mod.email  # Fetch moderator's email
    user_email = user.email  # Get the logged-in user's email
    user_name = user.name  # Get full name of the user
    
    Accept_Request.objects.create(request=request_obj, user=user)  # Create an entry in the Accept_Request table
    subject = "New Blood Donation Volunteer"
    message = f"""
    Dear {request_obj.mod.name}, 

    A user has volunteered for the blood donation request: 

    - **Volunteer Name:** {user_name}
    - **Volunteer Email:** {user_email}
    - **Request Title:** {request_obj.title}
    -**Blood Group:** {request_obj.bloodgroup}
    - **Location:** {request_obj.location}
    - **Deadline:** {request_obj.deadline}
    
    Please contact the volunteer to proceed further.

    Regards, 
    Community Connect Team
    """

    # Send email
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['sanjayab6922@gmail.com'], fail_silently=False)

    # Alert message and redirect
    alert = "<script>alert('Thank you! You have successfully volunteered for the Blood Donation request. The Moderator will contact you soon!'); window.location.href='/userhome/';</script>"
    return HttpResponse(alert)

    # Logic for processing the accepted request (e.g., updating status, notifications, etc.)
   
   

# views.py
# from django.http import JsonResponse

# def ignore_request_ajax(request, request_id):
#     if request.method == "POST":
#         try:
#             # Get the request object
#             request_obj = Request.objects.get(id=request_id)
            
#             # Update its status or delete it depending on your requirements
#             request_obj.status = "ignored"  # or request_obj.delete()
#             request_obj.save()
            
#             return JsonResponse({"success": True})
#         except Exception as e:
#             return JsonResponse({"success": False, "error": str(e)})
#     return JsonResponse({"success": False})


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Request
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proceed_request(request, request_id):
    if request.method == "POST":
        request_obj = get_object_or_404(Request, id=request_id)
        request_obj.delete()  # Deletes the request for all users

        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.shortcuts import render, get_object_or_404
from .models import Request

def available_donors(request, request_id):
    # Get the specific request
    blood_request = get_object_or_404(Request, id=request_id)
    
    # Get volunteers for this specific request
    volunteers = Accept_Request.objects.filter(request=blood_request)
    
    context = {
        'blood_request': blood_request,
        'volunteers': volunteers
    }
    
    return render(request, 'available_donors.html', context)



def acceptvolunteer(request, id):
    accepted_request = get_object_or_404(Accept_Request, id=id)
    accepted_request.status = 'Approved'
    accepted_request.save()

    # Send Email Notification
    subject = "Blood Donation Request Approved ✅"
    message = f"Dear {accepted_request.user.name},\n\n"
    message += f"Congratulations! Your volunteer request for blood donation has been approved.\n\n"
    message += f"Request Details:\n"
    message += f"- Request Title: {accepted_request.request.title}\n"
    message += f"- Location: {accepted_request.request.location}\n"
    message += f"- Deadline: {accepted_request.request.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
    message += "Thank you for your support in saving lives!\n\n"
    message += "Best Regards,\nBlood Donation Team"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # Ensure this is configured in settings.py
        [accepted_request.user.email],  # Recipient email
        fail_silently=False,
    )

    return redirect('available_donors', request_id=accepted_request.request.id)

from django.http import JsonResponse
import json

def rejectvolunteer(request):
    print("rejectvolunteer view called")
    print("POST data:", request.POST)
    
    if request.method == 'POST':
        try:
            # Get the list of volunteer IDs
            volunteer_ids_json = request.POST.get('volunteer_ids', '[]')
            print(f"volunteer_ids_json: {volunteer_ids_json}")
            
            volunteer_ids = json.loads(volunteer_ids_json)
            print(f"Parsed volunteer_ids: {volunteer_ids}")
            
            if not volunteer_ids:
                print("No volunteer IDs provided")
                return JsonResponse({'status': 'error', 'message': 'No volunteer IDs provided'})
            
            # Process each volunteer
            processed_count = 0
            for volunteer_id in volunteer_ids:
                try:
                    # Get the volunteer
                    volunteer = Accept_Request.objects.get(id=volunteer_id)
                    
                    # Skip if already processed
                    if volunteer.status in ['Approved', 'Rejected']:
                        continue
                    
                    # Update status
                    volunteer.status = 'Rejected'
                    volunteer.request.status = 'COMPLETED'
                    volunteer.request.save()
                    volunteer.save()
                    
                    # Send email
                    subject = "Blood Donation Request Status Update"
                    message = f"Dear {volunteer.user.name},\n\n"
                    message += f"Thank you for your willingness to donate blood for the request: {volunteer.request.title}.\n\n"
                    message += f"We appreciate your generous offer, but we wanted to inform you that your volunteer request has been processed and we've found other donors for this particular request.\n\n"
                    message += f"Please continue to volunteer for future donation requests. Your commitment to helping others is truly valuable.\n\n"
                    message += "Thank you for your understanding and support!\n\n"
                    message += "Best Regards,\nBlood Donation Team"
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [volunteer.user.email],
                        fail_silently=False,
                    )
                    
                    processed_count += 1
                    
                except Exception as e:
                    # Log the error but continue processing others
                    print(f"Error processing volunteer {volunteer_id}: {str(e)}")
            
            return JsonResponse({
                'status': 'success', 
                'message': f'Processed {processed_count} volunteers successfully'
            })
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def accept_volunteer_ajax(request):
    if request.method == 'POST':
        volunteer_id = request.POST.get('volunteer_id')
        
        try:
            # Get the volunteer
            volunteer = Accept_Request.objects.get(id=volunteer_id)
            
            # Skip if already rejected
            if volunteer.status == 'Rejected':
                return JsonResponse({'status': 'error', 'message': 'Volunteer already rejected'})
            
            # Update status
            volunteer.status = 'Approved'
            volunteer.save()
            
            # Send acceptance email (reusing your existing email code)
            subject = "Blood Donation Request Approved ✅"
            message = f"Dear {volunteer.user.name},\n\n"
            message += f"Congratulations! Your volunteer request for blood donation has been approved.\n\n"
            message += f"Request Details:\n"
            message += f"- Request Title: {volunteer.request.title}\n"
            message += f"- Location: {volunteer.request.location}\n"
            message += f"- Deadline: {volunteer.request.deadline.strftime('%Y-%m-%d %H:%M')}\n\n"
            message += "Thank you for your support in saving lives!\n\n"
            message += "Best Regards,\nBlood Donation Team"
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [volunteer.user.email],
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'success', 'message': 'Volunteer approved successfully'})
            
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


#groupchat
def chat_room(request):
    try:
        user_id = request.session['user_id']
        user = Reg.objects.get(id=user_id)
    except Exception as e:
        print(e)
        return redirect('login')
    messages = ChatMessage.objects.all().order_by("-timestamp")[:50]
    return render(request, "com/chat_room.html", {"messages": messages, "user": user})


from django.shortcuts import render
import pandas as pd
import joblib
import os

# Load trained model
model_path=os.path.join("blood_donation_modell.pkl")
model = joblib.load(model_path)

def predict_eligibility(request):
    prediction = None
    
    if request.method == "POST":
        try:
            # Get form data
            data = {
                'Age': int(request.POST['age']),
                'Weight_kg': int(request.POST['weight']),
                'Hemoglobin_g_dL': float(request.POST['hemoglobin']),
                'Systolic_BP': int(request.POST['systolic_bp']),
                'Diastolic_BP': int(request.POST['diastolic_bp']),
                'Recent_Illness': int(request.POST['recent_illness']),
                'Chronic_Disease': int(request.POST['chronic_disease']),
                'Medications': int(request.POST['medications']),
                'Recent_Surgery': int(request.POST['recent_surgery']),
                'Pregnancy': int(request.POST['pregnancy']),
                'Last_Donation_Days': int(request.POST['last_donation_days']),
                'Travel_Malaria_Zone': int(request.POST['travel_malaria_zone'])
            }
            
            # Convert to DataFrame and make prediction
            df = pd.DataFrame([data])
            prediction = model.predict(df)[0]
            
        except Exception as e:
            prediction = f"Error: {str(e)}"
    
    return render(request, "predict.html", {"prediction": prediction})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def adpostrequests(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        location = request.POST.get('location')
        date = request.POST.get('date')
        time = request.POST.get('time')

        # Combine date and time to ensure correct format
        scheduled_datetime = timezone.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")

        # Save data to the database
        AdminRequest(
            title=title,
            description=description,
            location=location,
            date=scheduled_datetime.date(),
            time=scheduled_datetime.time()
        ).save()
        
        return redirect('viewadposts')

    return render(request, 'adpostrequests.html')

def viewadposts(request):
    now = timezone.now()
    
    # Filter posts to exclude expired ones
    posts = AdminRequest.objects.all().order_by('created_at')

    return render(request, 'viewadposts.html', {'posts': posts})

def pdelete_post(request, post_id):
    post = get_object_or_404(AdminRequest, id=post_id)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect('viewadposts')



from django.db.models import Q

def adreqlist(request):
    email = request.session.get('email')
    if not email:
        return HttpResponse('Unauthorized: No email found in session')

    now = timezone.now()
    try:
        user = Mod.objects.get(email=email)
    except Mod.DoesNotExist:
        return redirect('modlogin')

    # Fetch only future or ongoing AdminRequest posts (exclude expired ones)
    posts = AdminRequest.objects.filter(
        Q(date__gt=now.date()) | 
        (Q(date=now.date()) & Q(time__gte=now.time()))
    )

    # Track volunteered posts for the logged-in moderator (No filtering for rejected)
    volunteered_posts = [post.id for post in posts if user in post.volunteers.all()]

    return render(request, 'adreqlist.html', {
        'posts': posts,
        'volunteered_posts': volunteered_posts
    })


def volunteer_for_camp(request, camp_id):
    email = request.session.get('email')
    print(email)
    if not email:
        return HttpResponse('Unauthorized: No email found in session')

    try:
        user = Mod.objects.get(email=email)
        camp = get_object_or_404(AdminRequest, id=camp_id)

        # Add the moderator as a volunteer
        camp.volunteers.add(user)

        # Send email notification to the admin
        admin_email = 'codeknight000@gmail.com' # Ensure this is defined in settings.py
        subject = f"Volunteer Request for Blood Camp: {camp.title}"
        message = (
            f"Moderator {user.name} has volunteered for the following blood camp:\n\n"
            f"📍 Location: {camp.location}\n"
            f"📅 Date: {camp.date}\n"
            f"⏰ Time: {camp.time}\n\n"
            f"Moderator Contact: {user.email}"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [admin_email])

        messages.success(request, "Your volunteering request has been sent successfully!")
        return redirect('adreqlist')
    except Exception as e:
        return HttpResponse(f'Error: {e}')


from django.shortcuts import render, get_object_or_404
from .models import AdminRequest

def volunteer_list(request, post_id):
    admin_request = get_object_or_404(AdminRequest, id=post_id)
    
    # Fetch all volunteers (no exclusions, we want to list all)
    volunteers = admin_request.volunteers.all()
    
    return render(request, 'volunteer_list.html', {
        'volunteers': volunteers,
        'admin_request': admin_request,
    })
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import Mod

@csrf_exempt
def select_moderator(request, mod_id):
    if request.method == "POST":
        moderator = get_object_or_404(Mod, id=mod_id)
        admin_request_id = request.POST.get('admin_request_id')
        admin_request = get_object_or_404(AdminRequest, id=admin_request_id)
        
        # Move to approved_volunteers
        admin_request.approved_volunteers.add(moderator)
        # Optionally remove from volunteers (uncomment if needed)
        # admin_request.volunteers.remove(moderator)
        
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error"}, status=400)

@csrf_exempt
def reject_moderator(request, mod_id):
    if request.method == "POST":
        moderator = get_object_or_404(Mod, id=mod_id)
        admin_request_id = request.POST.get('admin_request_id')  # Pass this from frontend
        admin_request = get_object_or_404(AdminRequest, id=admin_request_id)
        
        # Remove from volunteers
        admin_request.volunteers.remove(moderator)
        
        return JsonResponse({"status": "success"})
    
    return JsonResponse({"status": "error"}, status=400)

    


from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core import serializers

def session_list(request):
    sessions = MentoringSession.objects.filter(created_by=request.user)
    data = serializers.serialize('json', sessions)
    return JsonResponse({'sessions': json.loads(data)})

@login_required
def session_create(request):
    data = json.loads(request.body)
    session = {
        'title': data.get('title'),
        'dateTime': data.get('dateTime'),
        'description': data.get('description'),
        'location': data.get('location'),
    }
    
    mentoring_session = MentoringSession.objects.create(
        title=session['title'],
        date_time=session['dateTime'],
        description=session['description'],
        location=session['location'],
        created_by=request.user
    )
    return JsonResponse({'status': 'success', 'session': {
        'pk': mentoring_session.pk,
        'title': mentoring_session.title,
        'dateTime': mentoring_session.date_time.isoformat(),
        'description': mentoring_session.description,
        'location': mentoring_session.location
    }})
    
def session_delete(request, pk):
    try:
        session = MentoringSession.objects.get(pk=pk, created_by=request.user)
        session.delete()
        return JsonResponse({'status': 'success'})
    except MentoringSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)


def adpostrequests2(request):
    """
    View to display the mentoring session creation form.
    """
    return render(request, 'adpostrequests2.html')

def viewadposts2(request):
    """
    View to display all mentoring sessions created by the logged-in user.
    """
    sessions = MentoringSession.objects.filter(created_by=request.user)
    return render(request, 'viewsessions.html', {'sessions': sessions})


# def set_mentor_email(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         request.session['mentor_email'] = email
#         return redirect('session_mentor')
#     return render(request, 'set_email.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.db import IntegrityError
from .models import Mod, Session_by_Mentor  # Import your Mod model

def session_mentor(request):
    # Get email from session
    mentor_email = request.session.get('email')
    
    if not mentor_email:
        return redirect('modlogin')

    try:
        # Get the Mod instance
        mentor = Mod.objects.get(email=mentor_email)
    except Mod.DoesNotExist:
        return render(request, 'session_mentor.html', {
            'sessions': [],
            'error': 'Mentor account not found'
        })

    if request.method == 'POST':
        if 'create' in request.POST:
            try:
                # Create new session with the Mod instance
                session = Session_by_Mentor(
                    session_type=request.POST.get('session_type'),
                    title=request.POST.get('title'),
                    date_time=request.POST.get('date_time'),
                    description=request.POST.get('description', ''),
                    location=request.POST.get('location', ''),
                    created_by=mentor  # Passing the Mod instance directly
                    
                )
                session.save()
                return redirect('session_mentor')
            except IntegrityError as e:
                return HttpResponse(f"Database error: {str(e)}", status=500)
            except Exception as e:
                return HttpResponse(f"Error: {str(e)}", status=500)
            
        elif 'delete' in request.POST:
            session_id = request.POST.get('session_id')
            try:
                session = get_object_or_404(Session_by_Mentor, pk=session_id, created_by=mentor)
                session.delete()
                print(f"Deleted session ID: {session_id}")
                return redirect('session_mentor')
            except Exception as e:
                print(f"Error deleting session: {str(e)}")
                return HttpResponse(f"Error deleting session: {str(e)}", status=500)
    
    # Get all sessions for this mentor
    sessions = Session_by_Mentor.objects.filter(created_by=mentor).order_by('-date_time')
    print(f"Found {sessions.count()} sessions for mentor")
    
    return render(request, 'session_mentor.html', {
        'sessions': sessions,
        'mentor': mentor  # Pass mentor to template if needed
    })


def view_sessionmentor(request):
    mentor_email = request.session.get('email')
    if not mentor_email:
        return redirect('login')

    sessions = Session_by_Mentor.objects.filter(
        created_by__email=mentor_email
    ).prefetch_related(
        'sessionparticipation_set'
    ).order_by('-date_time')

    # Add counts to each session
    for session in sessions:
        session.approved_count = session.sessionparticipation_set.filter(status='approved').count()
        session.pending_count = session.sessionparticipation_set.filter(status='requested').count()

    return render(request, 'view_sessionmentor.html', {
        'sessions': sessions,
        'mentor_name': request.session.get('mod_name', '')
    })

def approve_registration(request, reg_id, status):
    if not request.session.get('email'):
        return redirect('login')
        
    registration = get_object_or_404(SessionRegistration, id=reg_id, session__created_by__email=request.session['email'])
    registration.status = status
    registration.save()
    
    messages.success(request, f'Registration {status} successfully!')
    return redirect('view_sessionmentor')    

def browse_sessions(request):
    sessions = Session_by_Mentor.objects.filter(date_time__gte=timezone.now()).order_by('date_time')
    approved_sessions = []

    if request.session.get('email'):
        user = Reg.objects.get(email=request.session['email'])
        approved_sessions = SessionParticipation.objects.filter(
            user=user, status='approved'
        ).values_list('session_id', flat=True)

    return render(request, 'browse_sessions.html', {
        'sessions': sessions,
        'approved_sessions': approved_sessions
    })

def join_session(request, session_id):
    if not request.session.get('email'):
        return redirect('login')
    
    session = get_object_or_404(Session_by_Mentor, id=session_id)
    user = Reg.objects.get(email=request.session.get('email'))
    
    # Check if already joined
    if SessionParticipation.objects.filter(user=user, session=session).exists():
        messages.warning(request, 'You have already requested to join this session')
    else:
        SessionParticipation.objects.create(user=user, session=session)
        messages.success(request, 'Successfully requested to join the session')
    
    return redirect('browse_sessions')


def approve_participation(request, participation_id, status):
    if not request.session.get('email'):
        return redirect('login')
    
    participation = get_object_or_404(
        SessionParticipation, 
        id=participation_id,
        session__created_by__email=request.session['email']
    )
    participation.status = status
    participation.save()
    
    messages.success(request, f'Participation {status} successfully')
    return redirect('view_sessionmentor')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Session_by_Mentor, SessionParticipation, Reg

def session_detail(request, session_id):
    # Get the session or return 404
    session = get_object_or_404(Session_by_Mentor, id=session_id)
    
    # Initialize variables
    user_joined = False
    participation_status = None
    user = None
    
    # Check if user is logged in
    if 'user_email' in request.session:
        try:
            user = Reg.objects.get(email=request.session['user_email'])
            participation = SessionParticipation.objects.filter(
                user=user,
                session=session
            ).first()
            if participation:
                user_joined = True
                participation_status = participation.status
        except Reg.DoesNotExist:
            pass
    
    # Get approved participants
    approved_participants = session.sessionparticipation_set.filter(
        status='approved'
    ).select_related('user')
    
    # Get participant count
    participant_count = approved_participants.count()
    
    # Check if user can join (not already joined and session is in future)
    can_join = False
    if user and not user_joined and session.date_time > timezone.now():
        can_join = True
    
    context = {
        'session': session,
        'user_joined': user_joined,
        'participation_status': participation_status,
        'approved_participants': approved_participants,
        'participant_count': participant_count,
        'can_join': can_join,
        'user_name': request.session.get('user_name', ''),
    }
    
    return render(request, 'session_detail.html', context)



from .models import CreativeContent
from .forms import CreativeContentForm

def process_video_url(url):
    """
    Convert various video URLs to their embed format
    Focusing specifically on fixing YouTube URL issues
    """
    import re
    from urllib.parse import urlparse
    
    # For YouTube short links (youtu.be)
    youtube_short_pattern = r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]+)'
    youtube_short_match = re.search(youtube_short_pattern, url)
    if youtube_short_match:
        video_id = youtube_short_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # For standard YouTube links
    youtube_pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)'
    youtube_match = re.search(youtube_pattern, url)
    if youtube_match:
        video_id = youtube_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # For YouTube shorts
    youtube_shorts_pattern = r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]+)'
    shorts_match = re.search(youtube_shorts_pattern, url)
    if shorts_match:
        video_id = shorts_match.group(1)
        return f'https://www.youtube.com/embed/{video_id}'
    
    # If nothing matched, try a direct parse for youtu.be URLs
    parsed_url = urlparse(url)
    if 'youtu.be' in parsed_url.netloc:
        # Extract video ID from path, removing leading slash and any query parameters
        path = parsed_url.path.lstrip('/')
        video_id = path.split('?')[0]  # Remove query parameters
        if video_id:
            return f'https://www.youtube.com/embed/{video_id}'
    
    # Handle other video platforms (Vimeo, etc.) as needed
    
    # Return the original URL if no conversion was made
    return url

def post_creative_content(request):
    if 'email' in request.session:
        try:
            mod = Mod.objects.get(email=request.session['email'])
        except Mod.DoesNotExist:
            return redirect('modlogin')

        # Fetch the recent 10 creative posts by the moderator
        contents = CreativeContent.objects.filter(moderator=mod).order_by('-created_at')[:10]
        print(f"Found {contents.count()} creative posts for moderator: {mod.name}")

        if request.method == 'POST':
            form = CreativeContentForm(request.POST, request.FILES)
            if form.is_valid():
                content = form.save(commit=False)
                content.moderator = mod

                # Process video URL if provided
                if content.video_url:
                    original_url = content.video_url
                    content.video_url = process_video_url(content.video_url)
                    print(f"Original URL: {original_url}")
                    print(f"Processed URL: {content.video_url}")
                
                content.save()

                from django.urls import reverse
                redirect_url = reverse('creators')
                alert = f"<script> alert('Content Posted Successfully'); window.location.href='{redirect_url}';</script>"
                return HttpResponse(alert)
        else:
            form = CreativeContentForm()

        return render(request, 'post_creative_content.html', {
            'form': form,
            'contents': contents,  # Pass recent content to the template
        })
    
    else:
        return redirect('modlogin')


from django.shortcuts import render, get_object_or_404
from .models import CreativeContent
from django.db.models import Q

def view_creative_content(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', '')
    user_id = request.session.get('user_id')

    contents = CreativeContent.objects.all().order_by('-created_at')

    if query:
        contents = contents.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if filter_type:
        contents = contents.filter(content_type=filter_type)

    content_with_likes_info = []
    for item in contents:
        user_has_liked = item.likes.filter(user_id=user_id).exists() if user_id else False
        content_with_likes_info.append({
            'item': item,
            'user_has_liked': user_has_liked
        })

    return render(request, 'view_creative_content.html', {
        'content_with_likes_info': content_with_likes_info,
        'query': query,
        'filter_type': filter_type,
        'user_id': user_id  # pass this to template
    })



def like_content(request, content_id):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "You must be logged in to like content.")
        return redirect('login')

    user = Reg.objects.get(id=user_id)
    content = CreativeContent.objects.get(id=content_id)

    like, created = Like.objects.get_or_create(user=user, content=content)
    if created:
        content.like_count += 1
        content.save()

    return redirect('view_creative_content')


def creator_view(request):
    if 'email' not in request.session:
        return redirect('modlogin')

    mod = get_object_or_404(Mod, email=request.session['email'])
    contents = CreativeContent.objects.filter(moderator=mod)

    edit_post = None
    edit_form = None

    if request.method == 'POST' and 'edit_id' in request.POST:
        edit_post = get_object_or_404(CreativeContent, id=request.POST['edit_id'])
        edit_form = CreativeContentForm(request.POST, request.FILES, instance=edit_post)
        
        if edit_form.is_valid():
            # Access video_url from the form's cleaned_data
            if 'video_url' in edit_form.cleaned_data and edit_form.cleaned_data['video_url']:
                original_url = edit_form.cleaned_data['video_url']
                processed_url = process_video_url(original_url)
                print(f"Original URL: {original_url}")
                print(f"Processed URL: {processed_url}")
                # Save the processed URL back to the form before saving
                form_instance = edit_form.save(commit=False)
                form_instance.video_url = processed_url
                form_instance.save()
                messages.success(request, "Post updated successfully.")
                return redirect('creator_view')
            else:
                # Save the form without processing the URL
                edit_form.save()
                messages.success(request, "Post updated successfully.")
                return redirect('creator_view')
        
    elif request.method == 'GET' and 'edit' in request.GET:
        edit_post = get_object_or_404(CreativeContent, id=request.GET['edit'])
        edit_form = CreativeContentForm(instance=edit_post)

    return render(request, 'creator_view.html', {
        'contents': contents,
        'edit_post': edit_post,
        'edit_form': edit_form,
    })




def delete_post(request, post_id):
    if 'email' not in request.session:
        return redirect('modlogin')

    try:
        post = CreativeContent.objects.get(id=post_id)
        if post.moderator.email != request.session['email']:
            return HttpResponseForbidden("You are not allowed to delete this post.")
        post.delete()
        messages.success(request, "Content deleted successfully.")
    except CreativeContent.DoesNotExist:
        messages.error(request, "Post not found.")

    return redirect('creator_view')



def book_resources(request):
    return render(request, 'book.html')

def video_resources(request):
    return render(request, 'video.html')

def article_resources(request):
    return render(request, 'article.html')


def Addfeedback(request):
    try:
        id= request.session['user_id']
        use= Reg.objects.get(id=id)
    except Exception as e:
        return redirect('login')
    if request.method == 'POST':
        choice = request.POST.get('name')
        feedback = request.POST.get('feedback')
        rating=request.POST.get('rating')

        if not feedback or not rating or not feedback:
            alert="<script>alert('All fields are required.'); window.location.href='/Addfeedback/';</script>"
            return HttpResponse(alert)

        try:
            Feedback.objects.create(choice=choice, rating=rating, description=feedback,usser=use)
            alert="<script>alert('Feedback submitted successfully'); window.location.href='/userhome/';</script>"
            return HttpResponse(alert)
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('Addfeedback')

    return render(request, 'Addfeedback.html')
    





