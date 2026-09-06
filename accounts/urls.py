from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_student, name='register'),
    path('register/instructor/', views.register_instructor, name='register_instructor'),
    path('instructor/pending-approval/', views.instructor_pending_approval, name='instructor_pending_approval'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('instructor/<str:username>/', views.instructor_profile, name='instructor_profile'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]


