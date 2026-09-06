from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('categories/', views.categories_list, name='categories_list'),
    path('compiler/', views.code_compiler, name='code_compiler'),
    path('live-classes/', views.live_classes, name='live_classes'),
    path('placements/', views.placement_portal, name='placement_portal'),
    path('projects/', views.projects_portal, name='projects_portal'),
    path('placements/job/<int:job_id>/', views.job_detail, name='job_detail'),

    path('placements/job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('courses/', views.course_list, name='course_list'),



    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:course_slug>/learn/', views.lesson_player, name='lesson_player'),
    path('course/<slug:course_slug>/learn/<int:lesson_id>/', views.lesson_player, name='lesson_player_lesson'),
    path('quiz/<int:quiz_id>/take/', views.quiz_take, name='quiz_take'),
    path('certificate/<int:enrollment_id>/download/', views.download_certificate, name='download_certificate'),
    path('wishlist/toggle/<int:course_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('review/add/<int:course_id>/', views.add_review, name='add_review'),
    path('discussion/post/<int:course_id>/', views.post_discussion, name='post_discussion'),
    path('discussion/post/<int:course_id>/<int:lesson_id>/', views.post_discussion, name='post_discussion_lesson'),
    path('discussion/<int:discussion_id>/reply/', views.reply_discussion, name='reply_discussion'),
    path('discussion/board/<int:course_id>/', views.discussion_board, name='discussion_board'),
    path('certificate/<int:certificate_id>/verify/', views.certificate_verify, name='certificate_verify'),
    path('instructor/<str:name_slug>/', views.instructor_profile, name='instructor_profile'),
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('interview-questions/', views.interview_questions_list, name='interview_questions_list'),
    path('interview-questions/manage/', views.manage_interview_questions, name='manage_interview_questions'),
    path('interview-questions/<int:question_id>/delete/', views.delete_interview_question, name='delete_interview_question'),
    path('feedback/submit/', views.submit_student_feedback, name='submit_student_feedback'),
]



