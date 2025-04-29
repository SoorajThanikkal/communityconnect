from django.db import models
from django.shortcuts import render




class Reg(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(max_length=50,unique=True)
    passw=models.CharField(max_length=50) 
    contact=models.CharField(max_length=10)
    age=models.CharField(max_length=5)
    location=models.CharField(max_length=50,default='India')
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    genderchoice=(
        ('male','MALE'),
        ('female','FEMALE'),
        ('others','OTHERS')
    )
    
    gender=models.CharField(max_length=10,choices=genderchoice,null=True,blank=True)
    
    bloodgroupchoice=(
        ('A+','A+'),
        ('A-','A-'),
        ('B+','B+'),
        ('B-','B-'),
        ('AB+','AB+'),
        ('AB-','AB-'),
        ('O+','O+'),
        ('O-','O-'),
    )
    bloodgroup=models.CharField(max_length=5,choices=bloodgroupchoice,null=True,blank=True)
    
    def __str__(self):
       return self.name
    
    

class Mod(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(max_length=50,unique=True)
    passw=models.CharField(max_length=50) 
    contact=models.CharField(max_length=10)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    bloodgroupchoice=(
        ('A+','A+'),
        ('A-','A-'),
        ('B+','B+'),
        ('B-','B-'),
        ('AB+','AB+'),
        ('AB-','AB-'),
        ('O+','O+'),
        ('O-','O-'),
    )
    bloodgroup=models.CharField(max_length=5,choices=bloodgroupchoice,null=True,blank=True)
            
    genderchoice=(
        ('male','MALE'),
        ('female','FEMALE'),
        ('others','OTHERS')
    )
    
    gender=models.CharField(max_length=10,choices=genderchoice,null=True,blank=True)
    
    categorychoice=(
        ('mentors and experts','MENTORS AND EXPERTS'),
        ('sponsors or donors','SPONSORS AND DONORS'),
        ('creators and sharers','CREATORS AND SHARERS'),
        
    )
    category=models.CharField(max_length=30,choices=categorychoice,null=False,blank=False)
    approval_status=models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)  
    

class Request(models.Model):
    mod=models.ForeignKey(Mod,on_delete=models.CASCADE)
    title=models.CharField(max_length=50)
    description=models.TextField()
    uploaded_at=models.DateTimeField(auto_now_add=True)
    location=models.CharField(max_length=50)
    bloodgroup=models.CharField(max_length=5,null=True,blank=True)
        
    deadline=models.DateTimeField()
    STATUS_CHOICES = (
        ('not received', 'NOT RECIEVED'),
        ('in progress', ' IN PROGRESS'),
        ('completed', 'COMPLETED'),
    )
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='not received')
    
    
    def __str__(self):
        return self.title
    
from django import forms
from .models import Request

class RequestForm(forms.ModelForm):
    class Meta:
        model = Request
        fields = ['title', 'description', 'location', 'deadline']
        widgets = {
            'deadline': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class Accept_Request(models.Model): 
    request=models.ForeignKey(Request,on_delete=models.CASCADE)
    user=models.ForeignKey(Reg,on_delete=models.CASCADE)
    STATUS_CHOICES = (
        ('Pending','Pending'),
        ('Approved', ' Approved'),
        ('Rejected', 'Rejected'),
    )
    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default='Pending')
    

from django.db import models
from django.utils import timezone

class AdminRequest(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    volunteers = models.ManyToManyField('Mod', blank=True, related_name="volunteered_camps")
    approved_volunteers = models.ManyToManyField('Mod', blank=True, related_name="approved_camps")
    
    def has_volunteered(self, user):
        return self.volunteers.filter(id=user.id).exists()


    @property
    def is_expired(self):
        """Check if the post has expired."""
        now = timezone.now()
        scheduled_datetime = timezone.datetime.combine(self.date, self.time)
        return scheduled_datetime < now

    def __str__(self):
        return self.title
    
    


#group chat
class ChatMessage(models.Model):
    sender = models.ForeignKey(Reg, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
 # admin post mentor session
class MentoringSession(models.Model):
    title = models.CharField(max_length=100)
    date_time = models.DateTimeField()
    description = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    class Meta:
        ordering = ['date_time']

    def __str__(self):
        return self.title
    

# moderator post mentor session
class Session_by_Mentor(models.Model):
    session_type=models.CharField(max_length=50,default='None',blank=True)
    title = models.CharField(max_length=200)
    date_time = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    location = models.URLField(help_text="Zoom or meet links", blank=True, null=True)
    created_by = models.ForeignKey(Mod, on_delete=models.CASCADE, related_name='mentor_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    participants = models.ManyToManyField(Reg, through='SessionParticipation', related_name='joined_sessions')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['date_time']   


# user register and view mentor session

class SessionRegistration(models.Model):
    session = models.ForeignKey(Session_by_Mentor, on_delete=models.CASCADE)
    user = models.ForeignKey(Reg, on_delete=models.CASCADE)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ), default='pending')
    
    class Meta:
        unique_together = ('session', 'user')
        
# user join to session
class SessionParticipation(models.Model):
    user = models.ForeignKey(Reg, on_delete=models.CASCADE)
    session = models.ForeignKey(Session_by_Mentor, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=(
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ), default='requested')
    
    
    
    
 

CONTENT_TYPES = [
    ('video', 'Video'),
    ('article', 'Article'),
    ('paper', 'Research Paper'),
    ('book', 'Book'),
    ('thought', 'Thought'),
    ('other', 'Other'),
]

class CreativeContent(models.Model):
    moderator = models.ForeignKey(Mod, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    description = models.TextField(help_text="Brief description or context")
    uploaded_file = models.FileField(upload_to='creative/files/', blank=True, null=True)
    video_url = models.URLField(blank=True, null=True, help_text="YouTube or external video link")
    thoughts = models.TextField(blank=True, null=True, help_text="Write something positive or motivational")
    created_at = models.DateTimeField(auto_now_add=True)
    like_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.title} ({self.get_content_type_display()}) by {self.moderator.name}"


class Like(models.Model):
    user = models.ForeignKey(Reg, on_delete=models.CASCADE)
    content = models.ForeignKey(CreativeContent, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content')
        
        
class Feedback(models.Model):
    description=models.TextField(max_length=50)
    rating=models.IntegerField()
    usser=models.ForeignKey(Reg,on_delete=models.CASCADE,null=True,blank=True)
    choice=models.CharField(max_length=50,null=True,blank=True)
    created_at= models.DateTimeField(auto_now=True)
    
    


