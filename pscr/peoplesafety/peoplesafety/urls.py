"""
URL configuration for peoplesafety project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from safetyapp import views
from safetyapp.views import emcontact, delete_contact,emergency,redirect_to_admin
from django.urls import path,include



urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pages (Just rendering templates)
    path('login/', views.loginpage, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/',views.registerpage,name='register'),
    path('forget/', views.forget, name='forget'),
    path('home/', views.home, name='home'),
   
    path('pofficial/',views.pofficial, name='pofficial'),
    path('viewreports/',views.vreports,name='viewreports'),
    path('dreport/<int:report_id>/', views.dreport, name='dreport'),
    
    
    path('track/',views.track,name='track'),
    path('emcontact/',views.emcontact,name='emcontact'),
    path('delete_contact/<int:contact_id>/', delete_contact, name='delete_contact'),
   

    # Form Submission Routes
    path('register-user/', views.register_view, name='register_user'),  # Handles registration form
    path('login-user/', views.login_view, name='login_user'),  # Handles login form
    path('logout/', views.logout_view, name='logout'),  # Handles logout
  
   path("send-otp/", views.send_otp, name="send_otp"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("reset-password/", views.reset_password, name="reset_password"),
    path('emcontact/',views.emergency,name='emergency'),

    path("",include("safetyapp.urls")),
    path('profile/',views.add_profile,name='profile'),
     path('admin-panel/', redirect_to_admin),

    
]
