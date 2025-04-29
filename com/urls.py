from django.urls import path
from .import views
from .views import volunteer_list, select_moderator, reject_moderator



urlpatterns = [
    path('',views.index , name='index'),
    path('index/',views.index , name='index'),
    path('register/',views.register,name='register'),
    path('otp/', views.otp, name='otp'),
    path('login/',views.login,name='login'),
    path('userhome/',views.userhome,name='userhome'),
    path('profile/',views.profile,name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('about/',views.about, name='about'),
    path('chatbot/',views.chatbot, name='chatbot'), 
    path('logout/',views.logout, name='logout'),
    path('contact',views.contact, name='contact'),
    path('modregister/',views.moderator, name='modregister'),
    path('modlogin/',views.modlogin, name='modlogin'),
    path('mod_approve/<int:pk>/',views.mod_approve, name='mod_approve'),
    path('mod_reject/<int:pk>/', views.mod_reject, name='mod_reject'),
    #path('modhome/',views.modhome, name='modhome'),
    path('mod_list/',views.mod_list, name='mod_list'),
    path('adminlogin/',views.adminlogin, name='adminlogin'),
    path('adminhome/',views.adminhome, name='adminhome'),
    path('modprofile/', views.modprofile, name='modprofile'),
    path('adminhome/userlist/',views.userlist, name='userlist'),
    path('delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('adminhome/moderatorlist/', views.moderatorlist, name='moderatorlist'),
    path('delete_mods/<int:user_id>/', views.delete_mods, name='delete_mods'),
    path('delete_useracc/', views.delete_useracc, name='delete_useracc'),
    path('mentors/', views.mentors, name='mentors'),
    path('sponsors/', views.sponsors, name='sponsors'),
    path('creators/', views.creators, name='creators'),
    path('upload_request/', views.upload_request, name='upload_request'),
    path('request_list/', views.request_list, name='request_list'),
    path('delete_request/<int:request_id>/', views.delete_request, name='delete_request'),
    path('addelete_request/<int:request_id>/', views.addelete_request, name='addelete_request'),
    path('delete_expired_request/<int:request_id>/', views.delete_expired_request, name='delete_expired_request'),
    path('viewrequests/', views.viewrequests, name='viewrequests'),
    path('modrequests/', views.request_list, name='modrequests'),
    path("forgot_password/", views.forgot_password, name="forgot_password"),
    path("verify_otp1/", views.verify_otp1, name="verify_otp1"),
    path("reset_password/", views.reset_password, name="reset_password"),
    path('forgot_password2/', views.forgot_password2, name='forgot_password2'),
    path('verify_otp2/', views.verify_otp2, name='verify_otp2'),
    path('reset_password2/', views.reset_password2, name='reset_password2'),
    path('edit_modprofile/', views.edit_modprofile, name='edit_modprofile'),
    path('accept/<int:request_id>/', views.accept, name='accept'),
    path('proceed/<int:request_id>/', views.proceed, name='proceed'),
    path('request/<int:request_id>/donors/', views.available_donors, name='available_donors'),
    #path('contact_donor/<int:donor_id>/<int:request_id>/', views.contact_donor, name='contact_donor'),
    path("volunteer_for_camp/<int:camp_id>/", views.volunteer_for_camp, name="volunteer_for_camp"),
    path("adreqlist/", views.adreqlist, name="adreqlist"),
    path("adpostrequests/", views.adpostrequests, name="adpostrequests"),
    path("adpostrequests2/", views.adpostrequests2, name="adpostrequests2"),
    path('viewadposts/', views.viewadposts, name='viewadposts'),
    path('viewadposts2/', views.viewadposts2, name='viewadposts2'),
    
    path('pdelete_post/<int:post_id>/', views.pdelete_post, name='pdelete_post'),
     
    path('volunteer_list/<post_id>/', views.volunteer_list, name='volunteer_list'),
    path('select_moderator/<int:mod_id>/', views.select_moderator, name='select_moderator'),
     path('reject_moderator/<int:mod_id>/', views.reject_moderator, name='reject_moderator'),
   

    path("proceed-request/<int:request_id>/", views.proceed_request, name="proceed_request"),
    path("acceptvolunteer/<int:id>/", views.acceptvolunteer, name="acceptvolunteer"),
    path("rejectvolunteer/", views.rejectvolunteer, name="rejectvolunteer"),
    path('accept_volunteer_ajax/', views.accept_volunteer_ajax, name='accept_volunteer_ajax'),
    
    path('session_list/', views.session_list, name='session_list'),
    # path('api/session_list/', views.session_list, name='session_list'),
    path('api/sessions/create/', views.session_create, name='session_create'),
    path('api/sessions/delete/<int:pk>/', views.session_delete, name='session_delete'),
    path("chat_room/", views.chat_room, name="chat_room"), 
    path('predict/', views.predict_eligibility, name='predict_eligibility'),
    
    
    
    path('session_mentor/', views.session_mentor, name='session_mentor'),
    path('view_sessions/', views.view_sessionmentor, name='view_sessionmentor'),
    path('approve_registration/<int:reg_id>/<str:status>/', views.approve_registration, name='approve_registration'),
    path('sessions/', views.browse_sessions, name='browse_sessions'),
    path('sessions/<int:session_id>/join/', views.join_session, name='join_session'),
     path('sessions/<int:session_id>/', views.session_detail, name='session_detail'),
    path('participation/<int:participation_id>/<str:status>/', views.approve_participation, name='approve_participation'),
    
    path('post_creative_content/', views.post_creative_content, name='post_creative_content'),
    path('view_creative_content/', views.view_creative_content, name='view_creative_content'),
    path('like-content/<int:content_id>/', views.like_content, name='like_content'),
    path('creator_view/', views.creator_view, name='creator_view'),
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    
    path('book/', views.book_resources, name='book-resources'),
    path('video/', views.video_resources, name='video-resources'),
    path('article/', views.article_resources, name='article-resources'),
    
    path('Addfeedback/', views.Addfeedback, name='Addfeedback'),
    
    path('test-redis/', views.test_redis),
    



   
    

]
    

    

