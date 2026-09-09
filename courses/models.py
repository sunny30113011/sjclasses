from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    icon = models.CharField(max_length=50, default="fa-laptop-code", help_text="FontAwesome icon class name e.g. fa-code")
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ('All Levels', 'All Levels'),
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    instructor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses_taught')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    short_description = models.CharField(max_length=500)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    online_thumbnail_url = models.URLField(max_length=500, blank=True, null=True, help_text="External online image URL for course thumbnail")
    preview_video_url = models.URLField(blank=True, null=True, help_text="YouTube / Vimeo / Cloudinary embed or video link")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Effective selling price after discount")
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='All Levels')
    language = models.CharField(max_length=50, default='English')
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title) + "-" + str(uuid.uuid4())[:6]
        if not self.discount_price or self.discount_price == 0:
            self.discount_price = self.price
        super().save(*args, **kwargs)

    @property
    def display_thumbnail_url(self):
        if self.thumbnail:
            try:
                return self.thumbnail.url
            except Exception:
                pass
        if self.online_thumbnail_url:
            return self.online_thumbnail_url
        category_defaults = {
            'Cloud & DevOps': 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=800&auto=format&fit=crop',
            'Frontend & UI/UX': 'https://images.unsplash.com/photo-1633356122544-f134324a6cee?q=80&w=800&auto=format&fit=crop',
            'Data Science & AI': 'https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?q=80&w=800&auto=format&fit=crop',
            'Enterprise Software': 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?q=80&w=800&auto=format&fit=crop',
            'Security & Networking': 'https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=800&auto=format&fit=crop',
        }
        if self.category and self.category.name in category_defaults:
            return category_defaults[self.category.name]
        return 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=800&auto=format&fit=crop'


    @property
    def total_lessons(self):
        return Lesson.objects.filter(module__course=self).count()

    @property
    def total_duration(self):
        lessons = Lesson.objects.filter(module__course=self)
        return sum(l.duration_minutes for l in lessons if l.duration_minutes)

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum(r.rating for r in reviews) / reviews.count(), 1)
        return 5.0

    @property
    def total_students(self):
        return self.enrollments.count()

    @property
    def is_preview_direct_video(self):
        if not self.preview_video_url:
            return False
        url = self.preview_video_url.lower().strip()
        return 'res.cloudinary.com' in url or url.endswith('.mp4') or url.endswith('.webm') or url.endswith('.mov') or url.endswith('.m3u8')

    @property
    def get_preview_embed_url(self):
        if not self.preview_video_url:
            return ""
        url = self.preview_video_url.strip()
        if 'youtube.com/watch' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            video_id = params.get('v', [''])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0].split('/')[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        elif 'youtube.com/embed/' in url:
            return url
        return url

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"


class Lesson(models.Model):
    TYPE_CHOICES = [
        ('video', 'Video Lesson'),
        ('pdf', 'PDF Notes'),
        ('quiz', 'MCQ Quiz'),
        ('assignment', 'Assignment'),
    ]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='video')
    video_url = models.URLField(blank=True, null=True, help_text="Embed link or Direct Video URL")
    pdf_file = models.FileField(upload_to='course_notes/', blank=True, null=True)
    content_text = models.TextField(blank=True, null=True, help_text="Text content or lesson instructions")
    duration_minutes = models.PositiveIntegerField(default=10)
    order = models.PositiveIntegerField(default=1)
    is_free_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    @property
    def is_youtube_video(self):
        if not self.video_url:
            return False
        url = self.video_url.lower()
        return 'youtube.com' in url or 'youtu.be' in url

    @property
    def is_cloudinary_or_direct_video(self):
        if not self.video_url:
            return False
        url = self.video_url.lower()
        return 'res.cloudinary.com' in url or url.endswith('.mp4') or url.endswith('.webm') or url.endswith('.mov') or url.endswith('.m3u8')

    @property
    def is_cloudinary_console(self):
        if not self.video_url:
            return False
        return 'console.cloudinary.com' in self.video_url.lower()

    @property
    def get_embed_video_url(self):
        if not self.video_url:
            return ""
        url = self.video_url.strip()
        
        # YouTube URL parsing
        if 'youtube.com/watch' in url:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            params = urllib.parse.parse_qs(parsed.query)
            video_id = params.get('v', [''])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        elif 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[-1].split('?')[0].split('/')[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?rel=0&modestbranding=1"
        elif 'youtube.com/embed/' in url:
            return url
            
        return url


    def __str__(self):
        return f"{self.module.title} - Lesson {self.order}: {self.title}"



class Quiz(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=255)
    pass_percentage = models.PositiveIntegerField(default=60)

    def __str__(self):
        return f"Quiz: {self.title}"


class QuizQuestion(models.Model):
    OPTION_CHOICES = [
        ('A', 'Option A'),
        ('B', 'Option B'),
        ('C', 'Option C'),
        ('D', 'Option D'),
    ]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=OPTION_CHOICES)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Q: {self.question_text[:50]}"


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_attempts')
    score_percentage = models.FloatField(default=0.0)
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.score_percentage}%)"


class Assignment(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=255)
    description = models.TextField()
    max_marks = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions')
    submission_file = models.FileField(upload_to='assignments/', blank=True, null=True)
    answer_text = models.TextField(blank=True, null=True)
    marks_obtained = models.PositiveIntegerField(default=0)
    graded = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)
    feedback_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'course')

    @property
    def progress_percentage(self):
        total = Lesson.objects.filter(module__course=self.course).count()
        if total == 0:
            return 100
        completed = LessonProgress.objects.filter(enrollment=self, completed=True).count()
        return int((completed / total) * 100)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')


class Wishlist(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating} stars)"


class Discussion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='discussions')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='discussions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class DiscussionReply(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_instructor_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Reply by {self.user.username} on '{self.discussion.title}'"


class Certificate(models.Model):

    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)

    # Admin customizable fields
    student_name = models.CharField(max_length=200, blank=True, help_text="Custom student full name displayed on certificate.")
    course_title = models.CharField(max_length=255, blank=True, help_text="Custom course title displayed on certificate.")
    issue_date = models.DateField(blank=True, null=True, help_text="Custom issue date displayed on certificate.")
    duration_hours = models.IntegerField(blank=True, null=True, help_text="Custom duration in hours displayed on certificate.")
    instructor_name = models.CharField(max_length=200, blank=True, help_text="Custom instructor/signer name.")
    instructor_title = models.CharField(max_length=200, blank=True, help_text="Custom instructor/signer title.")

    @property
    def display_student_name(self):
        if self.student_name and self.student_name.strip():
            return self.student_name.strip()
        name = self.enrollment.student.get_full_name()
        return name if name else self.enrollment.student.username

    @property
    def display_course_title(self):
        if self.course_title and self.course_title.strip():
            return self.course_title.strip()
        return self.enrollment.course.title

    @property
    def display_issue_date(self):
        if self.issue_date:
            return self.issue_date
        return self.issued_at.date() if self.issued_at else None

    @property
    def display_duration_hours(self):
        if self.duration_hours is not None:
            return self.duration_hours
        return self.enrollment.course.total_duration or 40

    @property
    def display_instructor_name(self):
        if self.instructor_name and self.instructor_name.strip():
            return self.instructor_name.strip()
        return "SUNNY SIR"

    @property
    def display_instructor_title(self):
        if self.instructor_title and self.instructor_title.strip():
            return self.instructor_title.strip()
        return "FOUNDER & INSTRUCTOR"

    def __str__(self):
        return f"Certificate {self.certificate_number} for {self.display_student_name}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('general', 'General'),
        ('offer', 'Prize Offer / Discount'),
        ('course', 'Course Update'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='general')
    link = models.CharField(max_length=255, blank=True, null=True, help_text="Optional action link")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username}: {self.title}"


class BroadcastOffer(models.Model):
    AUDIENCE_CHOICES = [
        ('all_students', 'All Students'),
        ('all_users', 'All Users'),
        ('unenrolled', 'Students without Any Course'),
    ]

    title = models.CharField(max_length=255)
    message = models.TextField()
    offer_badge = models.CharField(max_length=50, default="Special Offer", help_text="e.g. 🎁 50% OFF, Mega Sale, Prize Offer")
    action_url = models.CharField(max_length=255, blank=True, null=True, help_text="Button URL e.g. /payments/all-access/")
    action_button_text = models.CharField(max_length=50, default="Claim Offer Now")
    target_audience = models.CharField(max_length=30, choices=AUDIENCE_CHOICES, default='all_students')
    sent_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_broadcasts')
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-sent_at']

    def __str__(self):
        return f"Broadcast: {self.title} ({self.recipient_count} recipients)"


class LiveClass(models.Model):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_classes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    meeting_link = models.URLField(help_text="Zoom, Google Meet, or Jitsi link")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['scheduled_at']

    def __str__(self):
        return f"Live: {self.title} ({self.course.title})"


class ProjectFile(models.Model):
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_files')
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name='project_files')
    title = models.CharField(max_length=255)
    tech_stack = models.CharField(max_length=255, default="Python 3 / Django / SQLite / HTML5")
    description = models.TextField(blank=True, default="Complete production-ready web application source code with database models and setup guide.")
    is_free_download = models.BooleanField(default=True, help_text="Allow free download for all registered students in Projects Portal")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00, help_text="Set price for paid project downloads (e.g. ₹299)")
    zip_file = models.FileField(upload_to='project_zips/', help_text="Upload course project source code .zip file")
    file_size_mb = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    run_instructions = models.TextField(blank=True, default="""1. Extract the downloaded .ZIP file.
2. Open terminal inside the project directory.
3. Create virtual environment: python -m venv venv
4. Activate venv: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)
5. Install dependencies: pip install -r requirements.txt
6. Run migrations: python manage.py migrate
7. Start server: python manage.py runserver""")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.zip_file and hasattr(self.zip_file, 'size'):
            self.file_size_mb = round(self.zip_file.size / (1024 * 1024), 2)
        super().save(*args, **kwargs)

    def __str__(self):
        title_str = self.course.title if self.course else "Standalone Project"
        return f"Zip: {self.title} ({title_str})"


class ProjectPurchase(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_purchases')
    project = models.ForeignKey(ProjectFile, on_delete=models.CASCADE, related_name='purchases')
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='project_purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'project')

    def __str__(self):
        status = "Approved" if self.is_approved else "Pending"
        return f"{self.student.username} - {self.project.title} ({status})"




class JobPlacement(models.Model):
    JOB_TYPES = (
        ('Full-Time', 'Full-Time'),
        ('Part-Time', 'Part-Time'),
        ('Internship', 'Internship'),
        ('Contract', 'Contract'),
    )

    title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    location = models.CharField(max_length=255, default='Pune / Solapur / Remote')
    job_type = models.CharField(max_length=20, choices=JOB_TYPES, default='Full-Time')
    salary_package = models.CharField(max_length=100, help_text="e.g. 4.5 LPA - 8.0 LPA")
    skills_required = models.CharField(max_length=500, help_text="e.g. Python, Django, HTML, CSS, SQL")
    experience_required = models.CharField(max_length=100, default='Freshers / 0-2 Years')
    official_apply_url = models.URLField(default='https://careers.tcs.com', help_text="Official company job portal link uploaded by Admin")
    description = models.TextField()
    application_deadline = models.DateField()

    is_active = models.BooleanField(default=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} at {self.company_name}"


class JobApplication(models.Model):
    STATUS_CHOICES = (
        ('Applied', 'Applied'),
        ('Shortlisted', 'Shortlisted'),
        ('Interviewing', 'Interviewing'),
        ('Selected', 'Selected'),
        ('Rejected', 'Rejected'),
    )

    job = models.ForeignKey(JobPlacement, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.FileField(upload_to='resumes/')
    github_portfolio = models.URLField(blank=True, null=True)
    cover_note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'student')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.student.username} -> {self.job.title}"


class PlacementRecord(models.Model):
    student_name = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    package_lpa = models.CharField(max_length=50)
    placed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} - {self.company_name} ({self.package_lpa})"


class InterviewQuestion(models.Model):
    DIFFICULTY_CHOICES = (
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    )
    
    CATEGORY_CHOICES = (
        ('Technical', 'Technical Round'),
        ('Coding', 'Coding / Hands-on'),
        ('System Design', 'System Architecture & Design'),
        ('HR / Behavioral', 'HR & Behavioral Round'),
    )

    company_name = models.CharField(max_length=150, help_text="e.g. TCS, Infosys, Wipro, Amazon, Google, Accenture")
    topic = models.CharField(max_length=150, help_text="e.g. Python, Django, React, SQL, Data Structures, AWS")
    question_text = models.TextField(help_text="The interview question")
    answer_text = models.TextField(help_text="Detailed sample answer, explanation, or code snippet")
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='Medium')
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='Technical')
    code_snippet = models.TextField(blank=True, null=True, help_text="Optional Python/Java/JS code example for this answer")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_featured = models.BooleanField(default=False, help_text="Highlight on Top Company Questions list")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.company_name}] {self.question_text[:60]}"


class StudentFeedback(models.Model):
    student_name = models.CharField(max_length=150)
    student_role_company = models.CharField(max_length=150, help_text="e.g. Placed @ TCS (7.0 LPA)")
    rating = models.IntegerField(default=5, help_text="Rating out of 5 stars")
    feedback_text = models.TextField()
    student_image = models.ImageField(upload_to='student_feedback/', blank=True, null=True)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student_name} - {self.student_role_company}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.email}"


class CarouselSlide(models.Model):
    title = models.CharField(max_length=255, help_text="Main heading of the slide (e.g. Learn Today,)")
    highlight_text = models.CharField(max_length=255, blank=True, null=True, help_text="Highlighted text in yellow (e.g. Build Tomorrow)")
    badge_text = models.CharField(max_length=100, default="SJ TECH CLASSES", help_text="Pill badge text")
    badge_icon = models.CharField(max_length=50, default="fa-rocket", help_text="FontAwesome icon (e.g. fa-rocket, fa-qrcode, fa-briefcase, fa-code)")
    description = models.TextField(help_text="Subtitle or description text")
    image = models.ImageField(upload_to='carousel_slides/', blank=True, null=True, help_text="Upload custom hero banner image (Cloudinary or local)")
    online_image_url = models.URLField(max_length=500, blank=True, null=True, help_text="Optional external image URL if not uploading file directly")
    primary_btn_text = models.CharField(max_length=100, default="Explore All Courses")
    primary_btn_url = models.CharField(max_length=255, default="/courses/")
    secondary_btn_text = models.CharField(max_length=100, blank=True, null=True, default="Placement Drive")
    secondary_btn_url = models.CharField(max_length=255, blank=True, null=True, default="/placements/")
    gradient_css = models.CharField(
        max_length=255,
        default="linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)",
        help_text="Background gradient CSS (e.g. linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%))"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lowest number appears first)")
    is_active = models.BooleanField(default=True, help_text="Enable or disable this slide on the home page")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']
        verbose_name = "Carousel Slide"
        verbose_name_plural = "Carousel Slides"

    def __str__(self):
        return f"Slide {self.order}: {self.title}"

    @property
    def display_image_url(self):
        if self.image:
            try:
                return self.image.url
            except Exception:
                pass
        if self.online_image_url:
            return self.online_image_url
        return "/static/images/hero1.jpg"


