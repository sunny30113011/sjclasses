from django.contrib import admin
from .models import (
    Category, Course, Module, Lesson, Enrollment, LessonProgress,
    Quiz, QuizQuestion, QuizAttempt, Wishlist, Review, Discussion,
    DiscussionReply, Notification, LiveClass, ProjectFile,
    JobPlacement, JobApplication, PlacementRecord, Certificate,
    InterviewQuestion, StudentFeedback, ContactMessage, BroadcastOffer,
    CarouselSlide
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'instructor', 'category', 'price', 'discount_price', 'level', 'is_published', 'created_at')
    list_filter = ('is_published', 'level', 'category')
    search_fields = ('title', 'description', 'instructor__username')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    list_filter = ('course',)
    search_fields = ('title', 'course__title')


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'module', 'lesson_type', 'duration_minutes', 'is_free_preview', 'order')
    list_filter = ('lesson_type', 'is_free_preview', 'module__course')
    search_fields = ('title', 'module__title')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('enrolled_at',)
    search_fields = ('student__username', 'course__title')


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'completed', 'completed_at')
    list_filter = ('completed',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'pass_percentage')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'correct_option')


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'quiz', 'score_percentage', 'passed', 'attempted_at')
    list_filter = ('passed',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'added_at')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'rating', 'created_at')
    list_filter = ('rating',)


@admin.register(Discussion)
class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'lesson', 'created_at')


@admin.register(DiscussionReply)
class DiscussionReplyAdmin(admin.ModelAdmin):
    list_display = ('user', 'discussion', 'is_instructor_reply', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('user__username', 'title', 'message')


@admin.register(LiveClass)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'scheduled_at', 'duration_minutes', 'is_active')
    list_filter = ('is_active',)


@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'uploaded_at')


@admin.register(JobPlacement)
class JobPlacementAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'salary_package', 'job_type', 'application_deadline', 'is_active')
    list_filter = ('job_type', 'is_active')


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'applied_at')
    list_filter = ('status',)


@admin.register(PlacementRecord)
class PlacementRecordAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'company_name', 'designation', 'package_lpa', 'placed_at')


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'display_student_name', 'display_course_title', 'display_issue_date', 'display_duration_hours', 'issued_at')
    search_fields = ('certificate_number', 'student_name', 'course_title', 'enrollment__student__username')
    list_filter = ('issued_at',)


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'topic', 'question_text', 'category', 'difficulty', 'is_featured', 'created_at')
    list_filter = ('company_name', 'category', 'difficulty', 'is_featured')
    search_fields = ('company_name', 'topic', 'question_text', 'answer_text')


@admin.register(StudentFeedback)
class StudentFeedbackAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_role_company', 'rating', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved')
    list_editable = ('is_approved',)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'read', 'created_at')
    list_filter = ('read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_editable = ('read',)


@admin.register(BroadcastOffer)
class BroadcastOfferAdmin(admin.ModelAdmin):
    list_display = ('title', 'offer_badge', 'target_audience', 'recipient_count', 'sent_by', 'sent_at')
    list_filter = ('target_audience', 'sent_at')
    search_fields = ('title', 'message')


@admin.register(CarouselSlide)
class CarouselSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'badge_text', 'created_at')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('title', 'highlight_text', 'description')

