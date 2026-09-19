from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.http import HttpResponse, Http404
from django.utils import timezone
from .models import (
    Course, Category, Module, Lesson, Enrollment, LessonProgress,
    Quiz, QuizQuestion, QuizAttempt, Assignment, AssignmentSubmission,
    Wishlist, Review, Discussion, Notification
)
from payments.models import Cart, Payment
from .utils import generate_pdf_certificate

def home(request):
    from accounts.models import User
    from .models import StudentFeedback, CarouselSlide
    featured_courses = Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('modules__lessons').order_by('-created_at')[:8]
    categories = Category.objects.all()[:6]
    total_students = Enrollment.objects.values('student').distinct().count() or 1200
    total_courses = Course.objects.filter(is_published=True).count() or 25
    
    # Query only real approved instructors from Database (exclude admins and dummy accounts)
    instructors = User.objects.filter(
        role=User.ROLE_INSTRUCTOR,
        is_instructor_approved=True
    ).exclude(
        username__in=['instructor', 'test_ins_player', 'test_pending_instructor', 'test_approved_instructor']
    ).exclude(
        username__startswith='test_'
    ).distinct().order_by('-date_joined')
    
    # Query student feedbacks dynamically from database
    student_feedbacks = StudentFeedback.objects.filter(is_approved=True).order_by('-created_at')

    # Query active carousel slides dynamically from database
    carousel_slides = CarouselSlide.objects.filter(is_active=True).order_by('order')

    context = {
        'courses': featured_courses,
        'featured_courses': featured_courses,
        'categories': categories,
        'total_students': total_students,
        'total_courses': total_courses,
        'instructors': instructors,
        'student_feedbacks': student_feedbacks,
        'carousel_slides': carousel_slides,
    }
    return render(request, 'courses/home.html', context)




def about(request):
    return render(request, 'pages/about.html')


def contact(request):
    if request.method == 'POST':
        from .models import ContactMessage
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )

        messages.success(request, f"Thank you {name}! Your message has been received. We will get back to you shortly.")
        return redirect('courses:contact')
    return render(request, 'pages/contact.html')


def categories_list(request):
    categories = Category.objects.all()
    return render(request, 'courses/categories_list.html', {'categories': categories})


def code_compiler(request):
    return render(request, 'courses/compiler.html')


def live_classes(request):
    from .models import LiveClass
    if not request.user.is_authenticated:
        live_classes = LiveClass.objects.filter(is_active=True)
    elif request.user.is_lms_admin():
        live_classes = LiveClass.objects.filter(is_active=True)
    elif request.user.is_instructor():
        live_classes = LiveClass.objects.filter(course__instructor=request.user, is_active=True)
    else:
        enrolled_course_ids = Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True)
        live_classes = LiveClass.objects.filter(course_id__in=enrolled_course_ids, is_active=True)
    return render(request, 'courses/live_classes.html', {'live_classes': live_classes})


def placement_portal(request):
    from .models import JobPlacement, PlacementRecord
    jobs = JobPlacement.objects.filter(is_active=True)
    recent_placements = PlacementRecord.objects.all()[:10]
    return render(request, 'courses/placement_portal.html', {'jobs': jobs, 'recent_placements': recent_placements})


def projects_portal(request):
    from .models import ProjectFile, Enrollment, ProjectPurchase
    projects = ProjectFile.objects.select_related('course').all().order_by('-uploaded_at')
    
    purchased_project_ids = []
    pending_project_ids = []
    enrolled_course_ids = []

    if request.user.is_authenticated:
        enrolled_course_ids = list(Enrollment.objects.filter(student=request.user).values_list('course_id', flat=True))
        purchased_project_ids = list(ProjectPurchase.objects.filter(student=request.user, is_approved=True).values_list('project_id', flat=True))
        pending_project_ids = list(ProjectPurchase.objects.filter(student=request.user, is_approved=False).values_list('project_id', flat=True))

    project_items = []
    for p in projects:
        is_paid = (not p.is_free_download) and (p.price > 0)
        is_approved = p.id in purchased_project_ids
        is_pending = p.id in pending_project_ids

        is_accessible = request.user.is_authenticated and (
            (not is_paid) or 
            is_approved or 
            request.user.is_lms_admin() or 
            (hasattr(request.user, 'is_all_access_valid') and request.user.is_all_access_valid()) or
            (p.course and (p.course.id in enrolled_course_ids or request.user == p.course.instructor))
        )

        project_items.append({
            'project': p,
            'is_paid': is_paid,
            'is_approved': is_approved,
            'is_pending': is_pending,
            'is_accessible': is_accessible,
        })

    return render(request, 'courses/projects_portal.html', {'project_items': project_items})





def job_detail(request, job_id):
    from .models import JobPlacement, JobApplication
    job = get_object_or_404(JobPlacement, id=job_id, is_active=True)
    has_applied = False
    application = None
    if request.user.is_authenticated:
        application = JobApplication.objects.filter(job=job, student=request.user).first()
        has_applied = application is not None

    return render(request, 'courses/job_detail.html', {'job': job, 'has_applied': has_applied, 'application': application})


@login_required
def apply_job(request, job_id):
    from .models import JobPlacement, JobApplication
    job = get_object_or_404(JobPlacement, id=job_id, is_active=True)
    if request.method == 'POST':
        resume = request.FILES.get('resume')
        github_portfolio = request.POST.get('github_portfolio')
        cover_note = request.POST.get('cover_note')

        if not resume:
            messages.error(request, "Please upload your resume (.pdf / .docx).")
            return redirect('courses:job_detail', job_id=job.id)

        app, created = JobApplication.objects.get_or_create(
            job=job,
            student=request.user,
            defaults={
                'resume': resume,
                'github_portfolio': github_portfolio,
                'cover_note': cover_note,
                'status': 'Applied'
            }
        )
        if created:
            messages.success(request, f"🎉 Application submitted successfully for {job.title} at {job.company_name}!")
        else:
            messages.info(request, "You have already applied for this job.")
    return redirect('courses:job_detail', job_id=job.id)





def course_list(request):
    courses = Course.objects.filter(is_published=True).select_related('instructor', 'category').prefetch_related('modules__lessons')
    categories = Category.objects.all()

    # Search filter
    query = request.GET.get('q')
    if query:
        courses = courses.filter(
            Q(title__icontains=query) | 
            Q(short_description__icontains=query) |
            Q(description__icontains=query)
        )

    # Category filter
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        courses = courses.filter(category=selected_category)

    # Level filter
    level = request.GET.get('level')
    if level:
        courses = courses.filter(level=level)

    # Price filter
    price_type = request.GET.get('price')
    if price_type == 'free':
        courses = courses.filter(discount_price=0)
    elif price_type == 'paid':
        courses = courses.filter(discount_price__gt=0)

    context = {
        'courses': courses,
        'categories': categories,
        'selected_category': selected_category,
        'query': query,
        'selected_level': level,
        'selected_price': price_type,
    }
    return render(request, 'courses/course_list.html', context)


def course_detail(request, slug):
    course = get_object_or_404(Course.objects.select_related('instructor', 'category'), slug=slug)
    modules = course.modules.prefetch_related('lessons').all()
    reviews = course.reviews.select_related('student').all()
    
    is_enrolled = False
    has_pending_payment = False
    in_cart = False
    in_wishlist = False

    if request.user.is_authenticated:
        has_active_all_access = hasattr(request.user, 'is_all_access_valid') and request.user.is_all_access_valid()
        has_course_payment = Payment.objects.filter(user=request.user, course=course, payment_status='Approved').exists()

        if has_active_all_access or has_course_payment:
            is_enrolled = True
        else:
            # If user had all-access pass but it expired, and no specific course payment, they are not enrolled
            if getattr(request.user, 'has_all_access', False) and not has_active_all_access and not has_course_payment:
                is_enrolled = False
            else:
                is_enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
            has_pending_payment = Payment.objects.filter(user=request.user, course=course, payment_status='Pending').exists()
        in_cart = Cart.objects.filter(user=request.user, course=course).exists()
        in_wishlist = Wishlist.objects.filter(student=request.user, course=course).exists()

    context = {
        'course': course,
        'modules': modules,
        'reviews': reviews,
        'is_enrolled': is_enrolled,
        'has_pending_payment': has_pending_payment,
        'in_cart': in_cart,
        'in_wishlist': in_wishlist,
    }
    return render(request, 'courses/course_detail.html', context)


@login_required
def lesson_player(request, course_slug, lesson_id=None):
    course = get_object_or_404(Course, slug=course_slug)
    
    has_active_all_access = hasattr(request.user, 'is_all_access_valid') and request.user.is_all_access_valid()
    has_course_payment = Payment.objects.filter(user=request.user, course=course, payment_status='Approved').exists()

    # Block if All-Access Pass has expired and student has no individual course purchase
    if getattr(request.user, 'has_all_access', False) and not has_active_all_access and not has_course_payment and not request.user.is_instructor():
        messages.warning(request, "⚠️ Your 1-Year All-Access Pass has expired. Please renew your pass to continue learning.")
        return redirect('payments:all_access_checkout')

    # Check enrollment or active all-access pass
    enrollment = Enrollment.objects.filter(student=request.user, course=course).first()
    if not enrollment and has_active_all_access:
        enrollment, _ = Enrollment.objects.get_or_create(student=request.user, course=course)

    is_course_instructor = (request.user == course.instructor) or request.user.is_instructor() or request.user.is_lms_admin()
    if not enrollment and not is_course_instructor:
        # Check if requested lesson is free preview
        if lesson_id:
            lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
            if not lesson.is_free_preview:
                messages.warning(request, "You must enroll in this course to access this lesson.")
                return redirect('courses:course_detail', slug=course.slug)
        else:
            messages.warning(request, "You must enroll in this course to access the content.")
            return redirect('courses:course_detail', slug=course.slug)

    modules = course.modules.prefetch_related('lessons').all()
    
    # Get active lesson
    if lesson_id:
        active_lesson = get_object_or_404(Lesson, id=lesson_id, module__course=course)
    else:
        first_module = modules.first()
        active_lesson = first_module.lessons.first() if first_module else None

    if not active_lesson:
        messages.error(request, "No lessons found in this course yet.")
        return redirect('courses:course_detail', slug=course.slug)

    # Mark lesson completed if requested
    if request.method == 'POST' and 'mark_complete' in request.POST and enrollment:
        progress, created = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=active_lesson)
        progress.completed = True
        progress.save()
        
        # Check overall course completion
        if enrollment.progress_percentage == 100 and not enrollment.is_completed:
            enrollment.is_completed = True
            enrollment.completed_at = timezone.now()
            enrollment.save()
            # Generate Certificate
            generate_pdf_certificate(enrollment)
            Notification.objects.create(
                user=request.user,
                title="Course Completed! 🎓",
                message=f"Congratulations! You have completed '{course.title}'. Your PDF certificate is now ready for download."
            )
            messages.success(request, "🎉 Congratulations! You completed 100% of this course. Your Certificate is unlocked!")

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({'status': 'ok', 'progress': enrollment.progress_percentage})

    # Completed lesson IDs for checkmarks
    completed_lesson_ids = []
    if enrollment:
        completed_lesson_ids = LessonProgress.objects.filter(
            enrollment=enrollment, completed=True
        ).values_list('lesson_id', flat=True)

    discussions = Discussion.objects.filter(course=course, lesson=active_lesson).order_by('-created_at')

    context = {
        'course': course,
        'modules': modules,
        'active_lesson': active_lesson,
        'enrollment': enrollment,
        'completed_lesson_ids': completed_lesson_ids,
        'discussions': discussions,
    }
    return render(request, 'courses/lesson_player.html', context)


@login_required
def quiz_take(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    course = quiz.lesson.module.course
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)

    questions = quiz.questions.all()
    if not questions.exists():
        messages.info(request, "This quiz currently has no questions.")
        return redirect('courses:lesson_player_lesson', course_slug=course.slug, lesson_id=quiz.lesson.id)

    if request.method == 'POST':
        correct_count = 0
        total_questions = questions.count()

        for q in questions:
            selected = request.POST.get(f'q_{q.id}')
            if selected == q.correct_option:
                correct_count += 1

        score_pct = round((correct_count / total_questions) * 100, 1)
        passed = score_pct >= quiz.pass_percentage

        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            student=request.user,
            score_percentage=score_pct,
            passed=passed
        )

        if passed:
            progress, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=quiz.lesson)
            progress.completed = True
            progress.save()
            messages.success(request, f"🎉 You passed the quiz with {score_pct}%! Lesson marked complete.")
        else:
            messages.error(request, f"You scored {score_pct}%. You need at least {quiz.pass_percentage}% to pass. Please try again!")

        return render(request, 'courses/quiz_result.html', {
            'quiz': quiz,
            'attempt': attempt,
            'questions': questions,
            'score_pct': score_pct,
            'passed': passed,
            'course': course,
        })

    return render(request, 'courses/quiz_take.html', {'quiz': quiz, 'questions': questions, 'course': course})


@login_required
def download_certificate(request, enrollment_id):
    if request.user.is_lms_admin() or request.user.is_instructor():
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    else:
        enrollment = get_object_or_404(Enrollment, id=enrollment_id, student=request.user)
    
    cert, message = generate_pdf_certificate(enrollment, force=True)
    if cert and cert.pdf_file:
        cert.pdf_file.open('rb')
        response = HttpResponse(cert.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Certificate_{cert.certificate_number}.pdf"'
        return response
    else:
        messages.error(request, f"Failed to generate certificate: {message}")
        return redirect('dashboard:student_dashboard')



@login_required
def toggle_wishlist(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    wishlist_item = Wishlist.objects.filter(student=request.user, course=course).first()
    if wishlist_item:
        wishlist_item.delete()
        messages.info(request, f"Removed '{course.title}' from your wishlist.")
    else:
        Wishlist.objects.create(student=request.user, course=course)
        messages.success(request, f"Added '{course.title}' to your wishlist ❤️")
    
    referer = request.META.get('HTTP_REFERER')
    return redirect(referer if referer else 'courses:course_detail', slug=course.slug)


@login_required
def add_review(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if request.method == 'POST':
        rating = int(request.POST.get('rating', 5))
        comment = request.POST.get('comment', '').strip()
        if comment:
            Review.objects.update_or_create(
                course=course,
                student=request.user,
                defaults={'rating': rating, 'comment': comment}
            )
            messages.success(request, "Thank you for reviewing this course!")
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def post_discussion(request, course_id, lesson_id=None):
    course = get_object_or_404(Course, id=course_id)
    lesson = get_object_or_404(Lesson, id=lesson_id) if lesson_id else None
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if title and content:
            Discussion.objects.create(
                course=course,
                lesson=lesson,
                user=request.user,
                title=title,
                content=content
            )
            messages.success(request, "Question posted to discussion board!")
            
    if lesson:
        return redirect('courses:lesson_player_lesson', course_slug=course.slug, lesson_id=lesson.id)
    return redirect('courses:course_detail', slug=course.slug)


@login_required
def reply_discussion(request, discussion_id):
    from .models import DiscussionReply
    discussion = get_object_or_404(Discussion, id=discussion_id)
    content = request.POST.get('content', '').strip()

    if request.method == 'POST' and content:
        is_instructor = request.user.is_instructor() or request.user.is_lms_admin()
        DiscussionReply.objects.create(
            discussion=discussion,
            user=request.user,
            content=content,
            is_instructor_reply=is_instructor
        )

        # Notify the original question poster if someone else replied
        if discussion.user != request.user:
            from .models import Notification
            role_label = "Instructor" if is_instructor else request.user.username
            Notification.objects.create(
                user=discussion.user,
                title="💬 New Reply to Your Question",
                message=f"{role_label} replied to your question: '{discussion.title}'"
            )

        messages.success(request, "Reply posted successfully!")

    # Redirect back to lesson or course
    if discussion.lesson:
        return redirect('courses:lesson_player_lesson', course_slug=discussion.course.slug, lesson_id=discussion.lesson.id)
    return redirect('courses:course_detail', slug=discussion.course.slug)


@login_required
def discussion_board(request, course_id):
    from .models import DiscussionReply
    course = get_object_or_404(Course, id=course_id)
    discussions = Discussion.objects.filter(course=course).select_related('user', 'lesson').prefetch_related('replies__user').order_by('-created_at')
    return render(request, 'courses/discussion_board.html', {
        'course': course,
        'discussions': discussions,
    })


def certificate_verify(request, certificate_id):
    """Public certificate verification page — accessible without login (QR scan)."""
    from .models import Certificate
    certificate = get_object_or_404(Certificate, id=certificate_id)
    enrollment = certificate.enrollment
    return render(request, 'courses/certificate_verify.html', {
        'certificate': certificate,
        'enrollment': enrollment,
        'student': enrollment.student,
        'course': enrollment.course,
    })


def instructor_profile(request, name_slug):
    """
    Public Instructor Profile view dynamically loading database instructors.
    Displays bio, ratings, skills, contact numbers, office hours, and taught courses.
    """
    from accounts.models import User
    
    slug_clean = name_slug.strip().lower()
    
    # Search database for matching instructor
    instructor_obj = (
        User.objects.filter(username__iexact=slug_clean).first() or
        User.objects.filter(first_name__icontains=slug_clean.split('-')[0]).first() or
        User.objects.filter(role=User.ROLE_INSTRUCTOR).first()
    )

    if not instructor_obj:
        raise Http404("Instructor profile not found.")

    courses = Course.objects.filter(instructor=instructor_obj, is_published=True).order_by('-created_at')

    # Static fallback dictionary for enriched metadata if available
    instructors_data = {
        'sunny-sir': {
            'slug': 'sunny-sir',
            'name': 'SUNNY SIR',
            'title': 'Founder & Lead Instructor',
            'badge': 'SS',
            'bg_class': 'warning',
            'border_color': '#f59e0b',
            'experience': '10+ Years',
            'rating': '4.9',
            'reviews_count': '450+',
            'students_count': '1,500+',
            'bio': 'Sunny Sir is the Founder of SJ TECH CLASSES with over 10 years of software development and teaching experience. Specializing in Full Stack Web Development, Python, Django 5, PostgreSQL, REST APIs, and Manual Payment Systems, he has successfully mentored over 1,500 students into top IT companies like TCS, Infosys, and Wipro.',
            'skills': ['Python 3.12', 'Django 5', 'PostgreSQL', 'REST APIs', 'Full Stack Development', 'System Architecture', 'UPI Payment Integration'],
            'email': 'sunnywaghmode8@gmail.com',
            'phone_primary': '+91 7218858764',
            'phone_secondary': '+91 9226238798',
            'office_hours': 'Mon - Sat: 10:00 AM - 7:00 PM IST',
            'location': 'Solapur, Maharashtra, India'
        }
    }

    meta = instructors_data.get(slug_clean, {})

    profile = {
        'name': meta.get('name', instructor_obj.get_full_name() or instructor_obj.username),
        'username': instructor_obj.username,
        'title': meta.get('title', instructor_obj.headline or 'Senior Tech Instructor'),
        'badge': (instructor_obj.first_name[:1] + instructor_obj.last_name[:1]).upper() if instructor_obj.first_name else instructor_obj.username[:2].upper(),
        'bg_class': meta.get('bg_class', 'warning'),
        'border_color': meta.get('border_color', '#f59e0b'),
        'experience': meta.get('experience', '5+ Years'),
        'rating': meta.get('rating', '4.9'),
        'reviews_count': meta.get('reviews_count', '300+'),
        'students_count': meta.get('students_count', f"{Enrollment.objects.filter(course__instructor=instructor_obj).count() or 150}+"),
        'bio': instructor_obj.bio or meta.get('bio', f"{instructor_obj.get_full_name() or instructor_obj.username} is a professional instructor at SJ TECH CLASSES."),
        'skills': meta.get('skills', [instructor_obj.headline or 'Software Development', 'Python', 'Django', 'Web Engineering']),
        'email': instructor_obj.email or meta.get('email', 'sunnywaghmode8@gmail.com'),
        'phone_primary': instructor_obj.phone_number or meta.get('phone_primary', '+91 9226238798'),
        'phone_secondary': meta.get('phone_secondary', '+91 7218858764'),
        'office_hours': meta.get('office_hours', 'Mon - Sat: 10:00 AM - 7:00 PM IST'),
        'location': meta.get('location', 'Solapur, Maharashtra, India')
    }

    all_instructors = User.objects.filter(Q(role=User.ROLE_INSTRUCTOR) | Q(role=User.ROLE_ADMIN)).distinct()

    return render(request, 'courses/instructor_profile.html', {
        'profile': profile,
        'courses': courses,
        'instructor_obj': instructor_obj,
        'all_instructors': all_instructors,
    })


@login_required
def notifications_list(request):
    """
    Dedicated Notification Center page.
    """
    filter_type = request.GET.get('filter', 'all')
    queryset = Notification.objects.filter(user=request.user)

    if filter_type == 'unread':
        queryset = queryset.filter(is_read=False)

    notifications = queryset.order_by('-created_at')

    return render(request, 'courses/notifications.html', {
        'notifications': notifications,
        'filter_type': filter_type,
    })


@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    next_url = request.META.get('HTTP_REFERER') or 'courses:notifications_list'
    return redirect(next_url)


@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read!")
    next_url = request.META.get('HTTP_REFERER') or 'courses:notifications_list'
    return redirect(next_url)


@login_required
def delete_notification(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()
    messages.info(request, "Notification cleared.")
    next_url = request.META.get('HTTP_REFERER') or 'courses:notifications_list'
    return redirect(next_url)


def interview_questions_list(request):
    """
    Public Top Company Interview Questions & Answers Bank for Students.
    """
    from .models import InterviewQuestion
    query = request.GET.get('q', '').strip()
    company = request.GET.get('company', '').strip()
    difficulty = request.GET.get('difficulty', '').strip()
    category = request.GET.get('category', '').strip()

    questions = InterviewQuestion.objects.all()

    if query:
        questions = questions.filter(
            Q(question_text__icontains=query) |
            Q(answer_text__icontains=query) |
            Q(topic__icontains=query) |
            Q(company_name__icontains=query)
        )

    if company:
        questions = questions.filter(company_name__iexact=company)

    if difficulty:
        questions = questions.filter(difficulty=difficulty)

    if category:
        questions = questions.filter(category=category)

    all_companies = InterviewQuestion.objects.values_list('company_name', flat=True).distinct()

    return render(request, 'courses/interview_questions.html', {
        'questions': questions,
        'query': query,
        'company': company,
        'difficulty': difficulty,
        'category': category,
        'all_companies': all_companies,
    })


@login_required
def manage_interview_questions(request):
    """
    Admin & Instructor Studio to upload and manage interview questions & answers.
    """
    if not (request.user.is_lms_admin() or request.user.is_instructor()):
        messages.error(request, "Access restricted to Admins and Instructors.")
        return redirect('courses:interview_questions_list')

    from .models import InterviewQuestion

    if request.method == 'POST':
        company_name = request.POST.get('company_name', '').strip()
        topic = request.POST.get('topic', '').strip()
        category = request.POST.get('category', 'Technical')
        difficulty = request.POST.get('difficulty', 'Medium')
        question_text = request.POST.get('question_text', '').strip()
        answer_text = request.POST.get('answer_text', '').strip()
        code_snippet = request.POST.get('code_snippet', '').strip()
        is_featured = 'is_featured' in request.POST

        if company_name and question_text and answer_text:
            iq = InterviewQuestion.objects.create(
                company_name=company_name,
                topic=topic or 'General',
                category=category,
                difficulty=difficulty,
                question_text=question_text,
                answer_text=answer_text,
                code_snippet=code_snippet or None,
                uploaded_by=request.user,
                is_featured=is_featured
            )
            messages.success(request, f"Interview Question for '{company_name}' uploaded successfully!")
            return redirect('courses:manage_interview_questions')

    questions = InterviewQuestion.objects.all().order_by('-created_at')
    return render(request, 'courses/manage_interview_questions.html', {'questions': questions})


@login_required
def delete_interview_question(request, question_id):
    if not (request.user.is_lms_admin() or request.user.is_instructor()):
        messages.error(request, "Access restricted.")
        return redirect('courses:interview_questions_list')

    from .models import InterviewQuestion
    iq = get_object_or_404(InterviewQuestion, id=question_id)
    comp = iq.company_name
    iq.delete()
    messages.info(request, f"Interview Question for '{comp}' deleted.")
    return redirect('courses:manage_interview_questions')


def submit_student_feedback(request):
    """
    Allow students and users to submit feedback / reviews for home page.
    """
    from .models import StudentFeedback
    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        student_role = request.POST.get('student_role_company', 'Student @ SJ TECH CLASSES').strip()
        rating = int(request.POST.get('rating', 5))
        feedback_text = request.POST.get('feedback_text', '').strip()

        if student_name and feedback_text:
            StudentFeedback.objects.create(
                student_name=student_name,
                student_role_company=student_role,
                rating=rating,
                feedback_text=feedback_text,
                is_approved=True
            )
            messages.success(request, f"Thank you {student_name}! Your feedback has been added to Student Reviews! ✨")
    return redirect('courses:home')




