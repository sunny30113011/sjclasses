from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from courses.models import Course, Category, Module, Lesson, Enrollment, Wishlist, Certificate, Notification, Quiz, QuizQuestion, BroadcastOffer
from payments.models import Payment, Coupon, AllAccessPlan
from accounts.decorators import instructor_required, admin_required


@login_required
def dashboard_router(request):
    if request.user.is_lms_admin():
        return redirect('dashboard:admin_dashboard')
    elif request.user.is_instructor():
        return redirect('dashboard:instructor_dashboard')
    elif getattr(request.user, 'is_pending_instructor', lambda: False)():
        return redirect('accounts:instructor_pending_approval')
    else:
        return redirect('dashboard:student_dashboard')


@login_required
def student_dashboard(request):
    from django.db.models import Avg
    from courses.models import LessonProgress, QuizAttempt
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    payments = Payment.objects.filter(user=request.user).select_related('course')
    wishlist = Wishlist.objects.filter(student=request.user).select_related('course')
    notifications = Notification.objects.filter(user=request.user)[:10]

    # Analytics queries
    completed_lessons_count = LessonProgress.objects.filter(enrollment__student=request.user, completed=True).count()
    quiz_attempts = QuizAttempt.objects.filter(student=request.user).select_related('quiz')
    quiz_attempts_count = quiz_attempts.count()
    avg_quiz_score = quiz_attempts.aggregate(avg=Avg('score_percentage'))['avg'] or 0.0
    avg_quiz_score = round(avg_quiz_score, 1)

    welcome_creds = request.session.pop('welcome_credentials', None)

    context = {
        'enrollments': enrollments,
        'payments': payments,
        'wishlist': wishlist,
        'notifications': notifications,
        'completed_lessons_count': completed_lessons_count,
        'quiz_attempts': quiz_attempts,
        'quiz_attempts_count': quiz_attempts_count,
        'avg_quiz_score': avg_quiz_score,
        'welcome_creds': welcome_creds,
    }
    return render(request, 'dashboard/student_dashboard.html', context)


@instructor_required
def instructor_dashboard(request):
    my_courses = Course.objects.filter(instructor=request.user)
    total_students = Enrollment.objects.filter(course__instructor=request.user).count()
    approved_payments = Payment.objects.filter(course__instructor=request.user, payment_status='Approved')
    total_earnings = approved_payments.aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'my_courses': my_courses,
        'total_students': total_students,
        'total_earnings': total_earnings,
    }
    return render(request, 'dashboard/instructor_dashboard.html', context)


@instructor_required
def create_course(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        short_description = request.POST.get('short_description')
        description = request.POST.get('description')
        price = request.POST.get('price', 0)
        discount_price = request.POST.get('discount_price', price)
        level = request.POST.get('level', 'All Levels')
        thumbnail = request.FILES.get('thumbnail')
        online_thumbnail_url = request.POST.get('online_thumbnail_url', '').strip()
        preview_video_url = request.POST.get('preview_video_url')

        # Validate thumbnail if uploaded
        if thumbnail:
            from payments.validators import validate_image_file
            valid_thumb, thumb_err = validate_image_file(thumbnail, max_size_mb=5)
            if not valid_thumb:
                messages.error(request, f"Thumbnail Upload Error: {thumb_err}")
                return render(request, 'dashboard/create_course.html', {'categories': categories})

        category = get_object_or_404(Category, id=category_id) if category_id else None

        course = Course.objects.create(
            instructor=request.user,
            title=title,
            category=category,
            short_description=short_description,
            description=description,
            price=price,
            discount_price=discount_price,
            level=level,
            thumbnail=thumbnail,
            online_thumbnail_url=online_thumbnail_url,
            preview_video_url=preview_video_url,
            is_published=True
        )
        messages.success(request, f"Course '{course.title}' created successfully! Now add modules & lessons.")
        return redirect('dashboard:manage_course_content', course_id=course.id)

    return render(request, 'dashboard/create_course.html', {'categories': categories})


@instructor_required
def manage_course_content(request, course_id):
    if request.user.is_lms_admin():
        course = get_object_or_404(Course, id=course_id)
    else:
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
    modules = course.modules.prefetch_related('lessons').all()


    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_module':
            module_title = request.POST.get('module_title')
            order = modules.count() + 1
            Module.objects.create(course=course, title=module_title, order=order)
            messages.success(request, f"Module '{module_title}' added.")
            
        elif action == 'add_lesson':
            module_id = request.POST.get('module_id')
            module = get_object_or_404(Module, id=module_id, course=course)
            lesson_title = request.POST.get('lesson_title')
            lesson_type = request.POST.get('lesson_type')
            video_url = request.POST.get('video_url')
            pdf_file = request.FILES.get('pdf_file')
            duration = request.POST.get('duration_minutes', 10)
            is_preview = 'is_free_preview' in request.POST

            lesson = Lesson.objects.create(
                module=module,
                title=lesson_title,
                lesson_type=lesson_type,
                video_url=video_url,
                pdf_file=pdf_file,
                duration_minutes=duration,
                is_free_preview=is_preview,
                order=module.lessons.count() + 1
            )

            if lesson_type == 'quiz':
                Quiz.objects.create(lesson=lesson, title=f"Quiz: {lesson_title}")

            messages.success(request, f"Lesson '{lesson_title}' added to Module '{module.title}'.")

        return redirect('dashboard:manage_course_content', course_id=course.id)

    return render(request, 'dashboard/manage_course_content.html', {'course': course, 'modules': modules})


@admin_required
def admin_dashboard(request):
    from courses.models import Certificate
    pending_payments = Payment.objects.filter(payment_status='Pending').select_related('user', 'course')
    all_payments = Payment.objects.all().select_related('user', 'course')[:20]
    total_revenue = Payment.objects.filter(payment_status='Approved').aggregate(total=Sum('amount'))['total'] or 0
    total_students = User.objects.filter(role=User.ROLE_STUDENT).count()
    total_courses = Course.objects.count()

    # Instructors management queries
    instructors_qs = User.objects.filter(role=User.ROLE_INSTRUCTOR).annotate(
        courses_count=Count('courses_taught', distinct=True)
    ).order_by('-date_joined')
    pending_instructors = instructors_qs.filter(is_instructor_approved=False)
    approved_instructors = instructors_qs.filter(is_instructor_approved=True)
    total_instructors = approved_instructors.count()
    pending_instructors_count = pending_instructors.count()

    coupons = Coupon.objects.all()
    enrollments = Enrollment.objects.all().select_related('student', 'course')

    # Certificate Search by ID / Certificate Number / Student / Course
    cert_query = request.GET.get('cert_query', '').strip()
    certificates = Certificate.objects.all().select_related('enrollment__student', 'enrollment__course')
    
    if cert_query:
        if cert_query.isdigit():
            certificates = certificates.filter(
                Q(id=int(cert_query)) | 
                Q(certificate_number__icontains=cert_query) |
                Q(enrollment__id=int(cert_query))
            )
        else:
            certificates = certificates.filter(
                Q(certificate_number__icontains=cert_query) |
                Q(enrollment__student__username__icontains=cert_query) |
                Q(enrollment__student__first_name__icontains=cert_query) |
                Q(enrollment__student__last_name__icontains=cert_query) |
                Q(enrollment__student__email__icontains=cert_query) |
                Q(enrollment__course__title__icontains=cert_query)
            )
    certificates = certificates.order_by('-issued_at')[:30]

    students = User.objects.filter(role=User.ROLE_STUDENT).order_by('username')
    courses = Course.objects.all().order_by('title')

    # Registered Students Management queries & search
    student_query = request.GET.get('student_query', '').strip()
    student_status = request.GET.get('student_status', 'ALL').strip()

    students_qs = User.objects.filter(role=User.ROLE_STUDENT).annotate(
        enrollments_count=Count('enrollments', distinct=True)
    ).order_by('-date_joined')

    if student_query:
        students_qs = students_qs.filter(
            Q(username__icontains=student_query) |
            Q(first_name__icontains=student_query) |
            Q(last_name__icontains=student_query) |
            Q(email__icontains=student_query) |
            Q(phone_number__icontains=student_query)
        )

    if student_status == 'ACTIVE':
        students_qs = students_qs.filter(is_active=True)
    elif student_status == 'INACTIVE':
        students_qs = students_qs.filter(is_active=False)
    elif student_status == 'ALL_ACCESS':
        students_qs = students_qs.filter(has_all_access=True)

    registered_students = students_qs
    active_students_count = User.objects.filter(role=User.ROLE_STUDENT, is_active=True).count()
    inactive_students_count = User.objects.filter(role=User.ROLE_STUDENT, is_active=False).count()
    all_access_students_badge_count = User.objects.filter(role=User.ROLE_STUDENT, has_all_access=True).count()

    # Analytics aggregates for graphs
    from django.db.models.functions import TruncMonth
    monthly_revenue = Payment.objects.filter(payment_status='Approved').annotate(month=TruncMonth('paid_on')).values('month').annotate(total=Sum('amount')).order_by('month')
    course_enrollments = Course.objects.annotate(student_count=Count('enrollments')).values('title', 'student_count').order_by('-student_count')[:10]
    course_revenue = Payment.objects.filter(payment_status='Approved').values('course__title').annotate(total=Sum('amount')).order_by('-total')[:10]

    all_access_plan = AllAccessPlan.get_plan()
    all_access_students_count = User.objects.filter(
        has_all_access=True
    ).filter(
        Q(all_access_valid_until__isnull=True) | Q(all_access_valid_until__gt=timezone.now())
    ).count()

    from courses.models import StudentFeedback
    student_feedbacks_admin = StudentFeedback.objects.all().order_by('-created_at')

    context = {
        'pending_payments': pending_payments,
        'all_payments': all_payments,
        'total_revenue': total_revenue,
        'total_students': total_students,
        'total_instructors': total_instructors,
        'pending_instructors_count': pending_instructors_count,
        'pending_instructors': pending_instructors,
        'approved_instructors': approved_instructors,
        'all_instructors': instructors_qs,
        'total_courses': total_courses,
        'coupons': coupons,
        'enrollments': enrollments,
        'certificates': certificates,
        'cert_query': cert_query,
        'students': students,
        'courses': courses,
        'registered_students': registered_students,
        'student_query': student_query,
        'student_status': student_status,
        'active_students_count': active_students_count,
        'inactive_students_count': inactive_students_count,
        'all_access_students_badge_count': all_access_students_badge_count,
        'monthly_revenue': monthly_revenue,
        'course_enrollments': course_enrollments,
        'course_revenue': course_revenue,
        'all_access_plan': all_access_plan,
        'all_access_students_count': all_access_students_count,
        'student_feedbacks_admin': student_feedbacks_admin,
    }

    return render(request, 'dashboard/admin_dashboard.html', context)


@admin_required
def admin_enroll_student_free(request):
    import uuid
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        course_id = request.POST.get('course_id')

        student = get_object_or_404(User, id=student_id, role=User.ROLE_STUDENT)
        course = get_object_or_404(Course, id=course_id)

        # Check if enrollment already exists
        if Enrollment.objects.filter(student=student, course=course).exists():
            messages.warning(request, f"Student '{student.username}' is already enrolled in '{course.title}'.")
        else:
            # Create approved payment record with amount 0.00 for audit
            payment = Payment.objects.create(
                user=student,
                course=course,
                amount=0.00,
                payment_status='Approved',
                utr=f'ADMIN_FREE_{uuid.uuid4().hex[:8].upper()}',
                screenshot=None,
                admin_note='Manually enrolled by Admin for free.'
            )

            # Create Enrollment
            enrollment = Enrollment.objects.create(student=student, course=course)

            # Send enrollment email
            try:
                from accounts.emails import send_course_enrollment_email
                send_course_enrollment_email(enrollment)
            except Exception:
                pass

            # Notify student
            Notification.objects.create(
                user=student,
                title="Course Unlocked by Admin 🔓",
                message=f"Congratulations! Admin has manually granted you free access to '{course.title}'!"
            )

            messages.success(request, f"Successfully enrolled student '{student.username}' in '{course.title}' for free!")

    return redirect('dashboard:admin_dashboard')


from accounts.emails import send_payment_approved_email, send_payment_rejected_email, send_course_enrollment_email

@admin_required
def approve_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if payment.payment_status != 'Approved':
        payment.payment_status = 'Approved'
        payment.save()

        item_title = "Purchased Product"

        # 1. Handle All-Access Pass Payment (Unlocks ALL courses)
        if payment.is_all_access:
            plan = AllAccessPlan.get_plan()
            duration = plan.duration_days if plan.duration_days else 365
            item_title = f"All-Access VIP Master Pass ({duration} Days Access)"
            student = payment.user
            student.has_all_access = True
            student.all_access_valid_until = timezone.now() + timedelta(days=duration)
            student.save(update_fields=['has_all_access', 'all_access_valid_until'])

            # Enroll student in all published courses
            published_courses = Course.objects.filter(is_published=True)
            for c in published_courses:
                enrollment, _ = Enrollment.objects.get_or_create(student=student, course=c)
                try:
                    send_course_enrollment_email(enrollment)
                except Exception:
                    pass

            valid_date_str = student.all_access_valid_until.strftime('%d %b %Y')
            Notification.objects.create(
                user=student,
                title="🎉 All-Access 1-Year Pass Approved! 🔓",
                message=f"Hooray! Your All-Access payment (UTR: {payment.utr}) has been approved by Admin! You now have 1-Year full access to ALL {published_courses.count()} courses on SJ TECH CLASSES (Valid until {valid_date_str}).",
                notification_type='offer',
                link='/dashboard/'
            )
            try:
                send_payment_approved_email(payment)
            except Exception:
                pass

            messages.success(request, f"🎉 All-Access Pass APPROVED for student {student.username}! All {published_courses.count()} courses unlocked for 1 Year (valid until {valid_date_str}).")
            return redirect('dashboard:admin_dashboard')

        # 2. Handle Single Course Enrollment
        if payment.course:
            enrollment, _ = Enrollment.objects.get_or_create(student=payment.user, course=payment.course)
            send_course_enrollment_email(enrollment)
            item_title = payment.course.title

        # 3. Handle Project Purchase Approval if project payment
        from courses.models import ProjectPurchase
        project_purchases = ProjectPurchase.objects.filter(payment=payment)
        if project_purchases.exists():
            project_purchases.update(is_approved=True)
            first_p = project_purchases.first()
            if first_p and first_p.project:
                item_title = first_p.project.title

        # Notify student
        Notification.objects.create(
            user=payment.user,
            title="Payment Approved! 🔓",
            message=f"Great news! Your payment (UTR: {payment.utr}) for '{item_title}' has been approved by Admin!"
        )

        send_payment_approved_email(payment)

        messages.success(request, f"Payment #{payment.id} APPROVED! '{item_title}' is now unlocked for student {payment.user.username}.")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_unlock_all_courses_free(request):
    """
    1-Click Admin action to grant All-Access Pass to a student for free (valid for 1 year).
    """
    import uuid
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        student = get_object_or_404(User, id=student_id, role=User.ROLE_STUDENT)

        plan = AllAccessPlan.get_plan()
        duration = plan.duration_days if plan.duration_days else 365

        student.has_all_access = True
        student.all_access_valid_until = timezone.now() + timedelta(days=duration)
        student.save(update_fields=['has_all_access', 'all_access_valid_until'])

        published_courses = Course.objects.filter(is_published=True)
        enrolled_count = 0
        for course in published_courses:
            _, created = Enrollment.objects.get_or_create(student=student, course=course)
            if created:
                enrolled_count += 1

        Payment.objects.create(
            user=student,
            is_all_access=True,
            amount=0.00,
            payment_status='Approved',
            utr=f'ADMIN_ALL_ACCESS_{uuid.uuid4().hex[:8].upper()}',
            admin_note=f'All courses granted free by Admin for {duration} days (1 year)'
        )

        valid_date_str = student.all_access_valid_until.strftime('%d %b %Y')
        Notification.objects.create(
            user=student,
            title="🌟 All Courses 1-Year Pass Unlocked by Admin! 🔓",
            message=f"Congratulations! Admin has granted you a 1-Year All-Access Pass! All {published_courses.count()} courses on SJ TECH CLASSES are now completely unlocked for you until {valid_date_str}.",
            notification_type='offer',
            link='/courses/'
        )

        messages.success(request, f"🌟 Successfully granted 1-Year All-Access Pass to student '{student.username}'! Enrolled in {enrolled_count} courses (valid until {valid_date_str}).")
    return redirect('dashboard:admin_dashboard')


@admin_required
def toggle_all_access_offer(request):
    """
    Toggle All-Access Offer ON or OFF across the whole platform.
    """
    plan = AllAccessPlan.get_plan()
    plan.is_active = not plan.is_active
    plan.save(update_fields=['is_active'])

    status_str = "ACTIVATED (Visible across entire website)" if plan.is_active else "DEACTIVATED (Hidden from entire website)"
    messages.success(request, f"📢 All-Access Offer has been {status_str}!")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_update_all_access_plan(request):
    """
    Update All-Access Pass prices, duration, and details dynamically from Admin Panel.
    """
    if request.method == 'POST':
        plan = AllAccessPlan.get_plan()

        title = request.POST.get('title', '').strip()
        tagline = request.POST.get('tagline', '').strip()
        offer_price = request.POST.get('offer_price', '').strip()
        original_price = request.POST.get('original_price', '').strip()
        duration_days = request.POST.get('duration_days', '').strip()
        upi_id = request.POST.get('upi_id', '').strip()
        upi_number = request.POST.get('upi_number', '').strip()
        features = request.POST.get('features', '').strip()

        if title:
            plan.title = title
        if tagline:
            plan.tagline = tagline
        if offer_price:
            try:
                plan.offer_price = float(offer_price)
            except ValueError:
                messages.error(request, "Invalid offer price format.")
                return redirect('dashboard:admin_dashboard')
        if original_price:
            try:
                plan.original_price = float(original_price)
            except ValueError:
                messages.error(request, "Invalid original price format.")
                return redirect('dashboard:admin_dashboard')
        if duration_days:
            try:
                plan.duration_days = int(duration_days)
            except ValueError:
                messages.error(request, "Invalid duration days format.")
                return redirect('dashboard:admin_dashboard')
        if upi_id:
            plan.upi_id = upi_id
        if upi_number:
            plan.upi_number = upi_number
        if features:
            plan.features = features

        plan.save()
        messages.success(
            request, 
            f"✅ All-Access Plan settings updated successfully! Offer Price: ₹{plan.offer_price:.0f} (Original: ₹{plan.original_price:.0f}), Validity: {plan.duration_days} Days."
        )

    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_broadcast_offer(request):
    """
    Compose and send prize offer and discount announcements to students.
    """
    active_plan = AllAccessPlan.get_active_plan()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        offer_badge = request.POST.get('offer_badge', 'Special Offer').strip()
        action_url = request.POST.get('action_url', '').strip()
        action_button_text = request.POST.get('action_button_text', 'Claim Offer Now').strip()
        target_audience = request.POST.get('target_audience', 'all_students')

        if not title or not message:
            messages.error(request, "Please provide both a Title and Message for the offer.")
            return redirect('dashboard:broadcast_offer')

        # Determine recipient queryset
        if target_audience == 'all_users':
            recipients = User.objects.filter(is_active=True)
        elif target_audience == 'unenrolled':
            recipients = User.objects.filter(role=User.ROLE_STUDENT, is_active=True, enrollments__isnull=True).distinct()
        else: # all_students
            recipients = User.objects.filter(role=User.ROLE_STUDENT, is_active=True)

        count = recipients.count()

        # Bulk create Notification objects
        notifications_to_create = [
            Notification(
                user=recipient,
                title=f"{offer_badge}: {title}" if offer_badge else title,
                message=message,
                notification_type='offer',
                link=action_url or '/payment/all-access/'
            )
            for recipient in recipients
        ]
        Notification.objects.bulk_create(notifications_to_create)

        # Record BroadcastOffer in database
        BroadcastOffer.objects.create(
            title=title,
            message=message,
            offer_badge=offer_badge,
            action_url=action_url or '/payment/all-access/',
            action_button_text=action_button_text,
            target_audience=target_audience,
            sent_by=request.user,
            recipient_count=count
        )

        messages.success(request, f"🎉 Prize offer notification successfully broadcasted to {count} recipient(s)!")
        return redirect('dashboard:broadcast_offer')

    past_broadcasts = BroadcastOffer.objects.all().order_by('-sent_at')[:20]
    total_students_count = User.objects.filter(role=User.ROLE_STUDENT, is_active=True).count()
    unenrolled_count = User.objects.filter(role=User.ROLE_STUDENT, is_active=True, enrollments__isnull=True).distinct().count()

    context = {
        'past_broadcasts': past_broadcasts,
        'total_students_count': total_students_count,
        'unenrolled_count': unenrolled_count,
        'active_plan': active_plan,
    }
    return render(request, 'dashboard/broadcast_offer.html', context)



@admin_required
def reject_payment(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id)
    if request.method == 'POST':
        reason = request.POST.get('admin_note', 'Transaction reference or payment screenshot mismatch. Please try again or contact support.').strip()
        payment.payment_status = 'Rejected'
        payment.admin_note = reason
        payment.save()

        course_title = payment.course.title if payment.course else "Purchased Item"
        Notification.objects.create(
            user=payment.user,
            title="Payment Rejected ❌",
            message=f"Your payment for '{course_title}' was rejected. Reason: {reason}"
        )


        # Send Email Notification
        send_payment_rejected_email(payment)

        messages.info(request, f"Payment #{payment.id} REJECTED. Student notified.")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_generate_certificate(request, enrollment_id):
    from courses.utils import generate_pdf_certificate
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)
    
    cert, message = generate_pdf_certificate(enrollment, force=True) # Force generate by Admin
    if cert and cert.pdf_file:
        messages.success(request, f"Certificate {cert.certificate_number} generated for student {enrollment.student.username}!")
        cert.pdf_file.open('rb')
        response = HttpResponse(cert.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="Certificate_{cert.certificate_number}.pdf"'
        return response
    else:
        messages.error(request, f"Failed to generate certificate: {message}")
        return redirect('dashboard:admin_dashboard')


@admin_required
def admin_edit_certificate(request, certificate_id):
    """
    Allows Admin to edit any details on an issued certificate:
    - Certificate Number / ID
    - Custom Student Full Name
    - Custom Course Title
    - Custom Issue Date
    - Custom Duration in Hours
    - Custom Instructor / Signer Name & Title
    - Automatic PDF Re-rendering
    """
    certificate = get_object_or_404(Certificate, id=certificate_id)

    if request.method == 'POST':
        cert_num = request.POST.get('certificate_number', '').strip()
        student_name = request.POST.get('student_name', '').strip()
        course_title = request.POST.get('course_title', '').strip()
        issue_date_str = request.POST.get('issue_date', '').strip()
        duration_hours_str = request.POST.get('duration_hours', '').strip()
        instructor_name = request.POST.get('instructor_name', '').strip()
        instructor_title = request.POST.get('instructor_title', '').strip()
        regenerate_pdf = request.POST.get('regenerate_pdf') in ['1', 'on', 'true', 'True', True]

        # Validate unique certificate number if changed
        if cert_num and cert_num != certificate.certificate_number:
            if Certificate.objects.filter(certificate_number=cert_num).exclude(id=certificate.id).exists():
                messages.error(request, f"Certificate number '{cert_num}' is already assigned to another certificate.")
                return redirect('dashboard:admin_dashboard')
            certificate.certificate_number = cert_num

        certificate.student_name = student_name
        certificate.course_title = course_title
        certificate.instructor_name = instructor_name
        certificate.instructor_title = instructor_title

        if issue_date_str:
            from datetime import datetime
            try:
                certificate.issue_date = datetime.strptime(issue_date_str, '%Y-%m-%d').date()
            except ValueError:
                pass
        else:
            certificate.issue_date = None

        if duration_hours_str:
            try:
                certificate.duration_hours = int(duration_hours_str)
            except ValueError:
                pass
        else:
            certificate.duration_hours = None

        certificate.save()

        # Regenerate PDF if option selected (default: True)
        if regenerate_pdf:
            from courses.utils import generate_pdf_certificate
            generate_pdf_certificate(certificate.enrollment, force=True, notify_student=False)

        messages.success(
            request,
            f"✅ Certificate #{certificate.certificate_number} updated successfully"
            f"{' and PDF re-rendered with new details' if regenerate_pdf else ''}!"
        )

    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_regenerate_certificate(request, certificate_id):
    """
    1-click action to re-render the PDF certificate using the latest details.
    """
    certificate = get_object_or_404(Certificate, id=certificate_id)
    from courses.utils import generate_pdf_certificate
    cert, msg = generate_pdf_certificate(certificate.enrollment, force=True, notify_student=False)
    if cert and cert.pdf_file:
        messages.success(request, f"🔄 PDF for Certificate #{cert.certificate_number} regenerated successfully!")
    else:
        messages.error(request, f"Failed to regenerate certificate: {msg}")
    return redirect('dashboard:admin_dashboard')


@admin_required
def create_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').upper().strip()
        discount = request.POST.get('discount_percentage')
        if code and discount:
            Coupon.objects.create(code=code, discount_percentage=discount, active=True)
            messages.success(request, f"Coupon '{code}' with {discount}% discount created.")
    return redirect('dashboard:admin_dashboard')


@admin_required
def add_instructor(request):
    """
    Admin directly adds a new instructor with full profile details (approved by default).
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        headline = request.POST.get('headline', '').strip()
        bio = request.POST.get('bio', '').strip()
        upi_id = request.POST.get('upi_id', '').strip()
        is_approved = request.POST.get('is_instructor_approved') in ['on', 'true', 'True', '1', True]

        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required fields.")
            return redirect('dashboard:admin_dashboard')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already in use.")
        else:
            instructor = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=User.ROLE_INSTRUCTOR,
                is_instructor_approved=is_approved,
                phone_number=phone_number,
                headline=headline or "Instructor at SJ TECH CLASSES",
                bio=bio or "Technical Instructor & Mentor",
                upi_id=upi_id
            )
            messages.success(request, f"🎉 Instructor account '{instructor.username}' created and approved successfully!")
    return redirect('dashboard:admin_dashboard')


@admin_required
def edit_instructor(request, instructor_id):
    """
    Admin updates an instructor's details, credentials, and approval status.
    """
    instructor = get_object_or_404(User, id=instructor_id, role=User.ROLE_INSTRUCTOR)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        headline = request.POST.get('headline', '').strip()
        bio = request.POST.get('bio', '').strip()
        upi_id = request.POST.get('upi_id', '').strip()
        is_approved_val = request.POST.get('is_instructor_approved')
        new_password = request.POST.get('new_password', '').strip()

        if email and User.objects.filter(email=email).exclude(id=instructor.id).exists():
            messages.error(request, f"Email '{email}' is already registered to another account.")
            return redirect('dashboard:admin_dashboard')

        instructor.first_name = first_name
        instructor.last_name = last_name
        if email:
            instructor.email = email
        instructor.phone_number = phone_number
        instructor.headline = headline
        instructor.bio = bio
        instructor.upi_id = upi_id

        # Update approval status
        instructor.is_instructor_approved = is_approved_val in ['1', 'true', 'True', 'on', True]

        if new_password:
            instructor.set_password(new_password)

        instructor.save()
        messages.success(request, f"✅ Instructor '{instructor.username}' details updated successfully!")
    return redirect('dashboard:admin_dashboard')


@admin_required
def delete_instructor(request, instructor_id):
    """
    Admin deletes an instructor account safely reassigning their courses to Admin.
    """
    if request.method == 'POST':
        instructor = get_object_or_404(User, id=instructor_id, role=User.ROLE_INSTRUCTOR)
        username = instructor.username
        
        # Safely reassign any courses authored by this instructor to the Admin
        courses_reassigned = Course.objects.filter(instructor=instructor).update(instructor=request.user)

        instructor.delete()
        msg = f"🗑️ Instructor '{username}' has been deleted."
        if courses_reassigned > 0:
            msg += f" {courses_reassigned} authored course(s) were safely reassigned to your admin account."
        messages.success(request, msg)
    return redirect('dashboard:admin_dashboard')


@admin_required
def approve_instructor(request, instructor_id):
    """
    1-Click Admin action to approve a pending instructor application.
    """
    instructor = get_object_or_404(User, id=instructor_id, role=User.ROLE_INSTRUCTOR)
    instructor.is_instructor_approved = True
    instructor.save(update_fields=['is_instructor_approved'])

    Notification.objects.create(
        user=instructor,
        title="🎉 Instructor Account Approved! 🔓",
        message="Congratulations! Your Instructor application has been approved by the Admin! You now have full access to the Instructor Studio, Course Builder, and Live Classes.",
        notification_type='general',
        link='/dashboard/instructor/'
    )

    try:
        from accounts.emails import send_instructor_approved_email
        send_instructor_approved_email(instructor)
    except Exception:
        pass

    messages.success(request, f"🎉 Instructor '{instructor.username}' has been APPROVED! They now have full teaching access.")
    return redirect('dashboard:admin_dashboard')


@admin_required
def reject_instructor(request, instructor_id):
    """
    Admin revokes or rejects instructor access.
    """
    instructor = get_object_or_404(User, id=instructor_id, role=User.ROLE_INSTRUCTOR)
    instructor.is_instructor_approved = False
    instructor.save(update_fields=['is_instructor_approved'])

    Notification.objects.create(
        user=instructor,
        title="⚠️ Instructor Access Status Update",
        message="Your instructor access permissions have been revoked by the Administrator.",
        notification_type='general'
    )

    messages.warning(request, f"Instructor access for '{instructor.username}' has been revoked.")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_add_student(request):
    """
    Admin directly adds a new registered student with full profile details.
    """
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        password = request.POST.get('password', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        headline = request.POST.get('headline', '').strip()
        bio = request.POST.get('bio', '').strip()
        has_all_access = request.POST.get('has_all_access') in ['on', 'true', 'True', '1', True]
        is_active = request.POST.get('is_active', 'on') in ['on', 'true', 'True', '1', True]

        if not username or not email or not password:
            messages.error(request, "Username, email, and password are required fields.")
            return redirect('dashboard:admin_dashboard')

        if User.objects.filter(username=username).exists():
            messages.error(request, f"Username '{username}' is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, f"Email '{email}' is already registered.")
        else:
            student = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=User.ROLE_STUDENT,
                phone_number=phone_number,
                headline=headline or "Student at SJ TECH CLASSES",
                bio=bio or "",
                is_active=is_active,
                has_all_access=has_all_access,
                email_verified=True
            )
            if has_all_access:
                student.all_access_valid_until = timezone.now() + timedelta(days=365)
                student.save(update_fields=['all_access_valid_until'])

            messages.success(request, f"🎉 Student account '{student.username}' created successfully!")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_edit_student(request, student_id):
    """
    Admin updates a registered student's profile details, credentials, active status, or role.
    """
    student = get_object_or_404(User, id=student_id)
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        headline = request.POST.get('headline', '').strip()
        bio = request.POST.get('bio', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        role = request.POST.get('role', student.role).strip()
        is_active_val = request.POST.get('is_active') in ['1', 'true', 'True', 'on', True]
        has_all_access_val = request.POST.get('has_all_access') in ['1', 'true', 'True', 'on', True]
        email_verified_val = request.POST.get('email_verified') in ['1', 'true', 'True', 'on', True]

        # Check username uniqueness if changed
        if username and username != student.username:
            if User.objects.filter(username=username).exclude(id=student.id).exists():
                messages.error(request, f"Username '{username}' is already in use by another account.")
                return redirect('dashboard:admin_dashboard')
            student.username = username

        # Check email uniqueness if changed
        if email and email != student.email:
            if User.objects.filter(email=email).exclude(id=student.id).exists():
                messages.error(request, f"Email '{email}' is already registered to another account.")
                return redirect('dashboard:admin_dashboard')
            student.email = email

        # Prevent admin from deactivating or demoting their own admin account
        if student.id == request.user.id:
            if not is_active_val:
                messages.warning(request, "You cannot deactivate your own admin account.")
                is_active_val = True
            if role != User.ROLE_ADMIN and request.user.role == User.ROLE_ADMIN:
                messages.warning(request, "You cannot demote your own admin account.")
                role = User.ROLE_ADMIN

        student.first_name = first_name
        student.last_name = last_name
        student.phone_number = phone_number
        student.headline = headline
        student.bio = bio
        student.is_active = is_active_val
        student.email_verified = email_verified_val
        
        if role in [User.ROLE_STUDENT, User.ROLE_INSTRUCTOR, User.ROLE_ADMIN]:
            student.role = role
            if role == User.ROLE_INSTRUCTOR:
                student.is_instructor_approved = True

        # Handle All-Access pass toggle
        if has_all_access_val and not student.has_all_access:
            student.has_all_access = True
            if not student.all_access_valid_until or student.all_access_valid_until <= timezone.now():
                student.all_access_valid_until = timezone.now() + timedelta(days=365)
        elif not has_all_access_val and student.has_all_access:
            student.has_all_access = False

        if new_password:
            student.set_password(new_password)

        student.save()
        messages.success(request, f"✅ Student '{student.username}' details updated successfully!")
    return redirect('dashboard:admin_dashboard')


@admin_required
def admin_delete_student(request, student_id):
    """
    Admin deletes a registered student account safely.
    """
    if request.method == 'POST':
        student = get_object_or_404(User, id=student_id)
        
        # Prevent self deletion
        if student.id == request.user.id:
            messages.error(request, "⚠️ You cannot delete your own admin account.")
            return redirect('dashboard:admin_dashboard')

        username = student.username
        
        # If user is also an instructor with courses, reassign courses to current admin
        courses_reassigned = Course.objects.filter(instructor=student).update(instructor=request.user)

        student.delete()
        msg = f"🗑️ Registered student '{username}' has been deleted successfully."
        if courses_reassigned > 0:
            msg += f" {courses_reassigned} authored course(s) were safely reassigned to your admin account."
        messages.success(request, msg)
    return redirect('dashboard:admin_dashboard')



@instructor_required
def course_builder(request):
    if request.user.is_lms_admin():
        my_courses = Course.objects.all().prefetch_related('modules', 'live_classes', 'project_files')
    else:
        my_courses = Course.objects.filter(instructor=request.user).prefetch_related('modules', 'live_classes', 'project_files')
    return render(request, 'dashboard/course_builder.html', {'my_courses': my_courses})


@instructor_required
def schedule_live_class(request):
    from courses.models import LiveClass
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if request.user.is_lms_admin():
            course = get_object_or_404(Course, id=course_id)
        else:
            course = get_object_or_404(Course, id=course_id, instructor=request.user)

        title = request.POST.get('title')
        scheduled_at = request.POST.get('scheduled_at')
        duration_minutes = request.POST.get('duration_minutes', 60)
        meeting_link = request.POST.get('meeting_link')

        live_class = LiveClass.objects.create(
            course=course,
            title=title,
            scheduled_at=scheduled_at,
            duration_minutes=duration_minutes,
            meeting_link=meeting_link,
            is_active=True
        )
        try:
            from accounts.emails import send_live_class_alert_email
            send_live_class_alert_email(live_class, is_update=False)
        except Exception:
            pass
        messages.success(request, f"Live Class '{title}' scheduled successfully for '{course.title}'!")
    return redirect('dashboard:course_builder')


@instructor_required
def edit_live_class(request, live_class_id):
    from courses.models import LiveClass
    live_class = get_object_or_404(LiveClass, id=live_class_id)
    if not (request.user.is_lms_admin() or live_class.course.instructor == request.user):
        messages.error(request, "Unauthorized access to live class edit.")
        return redirect('dashboard:course_builder')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        scheduled_at = request.POST.get('scheduled_at')
        duration_minutes = request.POST.get('duration_minutes', 60)
        meeting_link = request.POST.get('meeting_link', '').strip()
        is_active = 'is_active' in request.POST

        if title and scheduled_at and meeting_link:
            live_class.title = title
            live_class.scheduled_at = scheduled_at
            live_class.duration_minutes = duration_minutes
            live_class.meeting_link = meeting_link
            live_class.is_active = is_active
            live_class.save()
            try:
                from accounts.emails import send_live_class_alert_email
                send_live_class_alert_email(live_class, is_update=True)
            except Exception:
                pass
            messages.success(request, f"Live Class '{live_class.title}' updated successfully! ✨")
            return redirect('dashboard:course_builder')
        else:
            messages.error(request, "Please fill in all required fields.")

    return render(request, 'dashboard/edit_live_class.html', {'live_class': live_class})


@instructor_required
def delete_live_class(request, live_class_id):
    from courses.models import LiveClass
    live_class = get_object_or_404(LiveClass, id=live_class_id)
    if not (request.user.is_lms_admin() or live_class.course.instructor == request.user):
        messages.error(request, "Unauthorized access to live class delete.")
        return redirect('dashboard:course_builder')

    title = live_class.title
    live_class.delete()
    messages.success(request, f"Live Class '{title}' deleted.")
    return redirect('dashboard:course_builder')


@instructor_required
def upload_project_zip(request):
    from courses.models import ProjectFile
    if request.method == 'POST':
        course_id = request.POST.get('course_id')
        if request.user.is_lms_admin():
            course = get_object_or_404(Course, id=course_id)
        else:
            course = get_object_or_404(Course, id=course_id, instructor=request.user)

        title = request.POST.get('title')
        zip_file = request.FILES.get('zip_file')

        if zip_file and zip_file.name.endswith('.zip'):
            ProjectFile.objects.create(
                course=course,
                title=title,
                zip_file=zip_file
            )
            messages.success(request, f"Project .ZIP file '{title}' uploaded for '{course.title}'!")
        else:
            messages.error(request, "Invalid file format. Only .zip files are allowed.")
    return redirect('dashboard:course_builder')



@login_required
def manage_placements(request):
    if not (request.user.is_lms_admin() or request.user.is_instructor()):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:student_dashboard')

    from courses.models import JobPlacement, JobApplication, PlacementRecord
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'post_job':
            title = request.POST.get('title')
            company_name = request.POST.get('company_name')
            location = request.POST.get('location')
            salary_package = request.POST.get('salary_package')
            skills_required = request.POST.get('skills_required')
            official_apply_url = request.POST.get('official_apply_url', 'https://careers.tcs.com')
            application_deadline = request.POST.get('application_deadline')
            description = request.POST.get('description')

            JobPlacement.objects.create(
                title=title,
                company_name=company_name,
                location=location,
                salary_package=salary_package,
                skills_required=skills_required,
                official_apply_url=official_apply_url,
                application_deadline=application_deadline,
                description=description
            )
            messages.success(request, f"Job Drive '{title}' at {company_name} published successfully!")


        elif action == 'add_record':
            student_name = request.POST.get('student_name')
            company_name = request.POST.get('company_name')
            designation = request.POST.get('designation')
            package_lpa = request.POST.get('package_lpa')

            PlacementRecord.objects.create(
                student_name=student_name,
                company_name=company_name,
                designation=designation,
                package_lpa=package_lpa
            )
            messages.success(request, f"Placed student record for {student_name} added to Hall of Fame!")
        return redirect('dashboard:manage_placements')

    applications = JobApplication.objects.all().select_related('job', 'student')
    jobs = JobPlacement.objects.all()

    return render(request, 'dashboard/manage_placements.html', {
        'applications': applications,
        'jobs': jobs
    })


@login_required
def update_application_status(request, application_id):
    if not (request.user.is_lms_admin() or request.user.is_instructor()):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:student_dashboard')

    from courses.models import JobApplication
    application = get_object_or_404(JobApplication, id=application_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            messages.success(request, f"Application for {application.student.username} updated to '{new_status}'.")
    return redirect('dashboard:manage_placements')


@instructor_required
def edit_course(request, course_id):
    if request.user.is_lms_admin():
        course = get_object_or_404(Course, id=course_id)
    else:
        course = get_object_or_404(Course, id=course_id, instructor=request.user)

    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        category_id = request.POST.get('category_id')
        short_desc = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        price = request.POST.get('price', 0)
        discount_price = request.POST.get('discount_price', 0)
        level = request.POST.get('level', 'Beginner')
        preview_video_url = request.POST.get('preview_video_url', '').strip()
        online_thumbnail_url = request.POST.get('online_thumbnail_url', '').strip()
        is_published = 'is_published' in request.POST
        thumbnail = request.FILES.get('thumbnail')

        if title and category_id:
            category = get_object_or_404(Category, id=category_id)
            course.title = title
            course.category = category
            course.short_description = short_desc
            course.description = description
            course.price = price
            course.discount_price = discount_price
            course.level = level
            course.preview_video_url = preview_video_url
            course.online_thumbnail_url = online_thumbnail_url
            course.is_published = is_published
            if thumbnail:
                course.thumbnail = thumbnail
            course.save()
            messages.success(request, f"Course '{course.title}' updated successfully! ✨")
            return redirect('dashboard:course_builder')

    return render(request, 'dashboard/edit_course.html', {'course': course, 'categories': categories})


@instructor_required
def delete_course(request, course_id):
    if request.user.is_lms_admin():
        course = get_object_or_404(Course, id=course_id)
    else:
        course = get_object_or_404(Course, id=course_id, instructor=request.user)

    if request.method == 'POST':
        title = course.title
        course.delete()
        messages.success(request, f"Course '{title}' has been deleted.")
        return redirect('dashboard:course_builder')

    return render(request, 'dashboard/delete_course_confirm.html', {'course': course})


@instructor_required
def edit_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not (request.user.is_lms_admin() or lesson.module.course.instructor == request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:course_builder')

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        lesson_type = request.POST.get('lesson_type', 'video')
        video_url = request.POST.get('video_url', '').strip()
        duration = request.POST.get('duration_minutes', 10)
        is_preview = 'is_free_preview' in request.POST
        pdf_file = request.FILES.get('pdf_file')

        if title:
            lesson.title = title
            lesson.lesson_type = lesson_type
            lesson.video_url = video_url
            lesson.duration_minutes = duration
            lesson.is_free_preview = is_preview
            if pdf_file:
                lesson.pdf_file = pdf_file
            lesson.save()
            messages.success(request, f"Lesson '{lesson.title}' updated successfully!")
            return redirect('dashboard:manage_course_content', course_id=lesson.module.course.id)

    return render(request, 'dashboard/edit_lesson.html', {'lesson': lesson})


@instructor_required
def delete_lesson(request, lesson_id):
    lesson = get_object_or_404(Lesson, id=lesson_id)
    if not (request.user.is_lms_admin() or lesson.module.course.instructor == request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:course_builder')

    course_id = lesson.module.course.id
    title = lesson.title
    lesson.delete()
    messages.success(request, f"Lesson '{title}' deleted.")
    return redirect('dashboard:manage_course_content', course_id=course_id)


@instructor_required
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    if not (request.user.is_lms_admin() or module.course.instructor == request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:course_builder')

    course_id = module.course.id
    title = module.title
    module.delete()
    messages.success(request, f"Module '{title}' and all its lessons deleted.")
    return redirect('dashboard:manage_course_content', course_id=course_id)


@instructor_required
def delete_project_file(request, project_id):
    from courses.models import ProjectFile
    project = get_object_or_404(ProjectFile, id=project_id)
    if not (request.user.is_lms_admin() or (project.course and project.course.instructor == request.user)):
        messages.error(request, "Unauthorized access.")
        return redirect('dashboard:course_builder')

    title = project.title
    project.delete()
    messages.success(request, f"Project file '{title}' deleted.")
    return redirect('dashboard:course_builder')


@instructor_required
def instructor_assignments(request):
    from courses.models import AssignmentSubmission
    submissions = AssignmentSubmission.objects.filter(
        assignment__lesson__module__course__instructor=request.user
    ).select_related('assignment', 'student', 'assignment__lesson__module__course').order_by('-submitted_at')
    
    return render(request, 'dashboard/assignments_studio.html', {'submissions': submissions})


@instructor_required
def grade_assignment(request, submission_id):
    from courses.models import AssignmentSubmission, Notification
    submission = get_object_or_404(AssignmentSubmission, id=submission_id)
    
    # Permission check: verify that the instructor owns the course this assignment belongs to
    course = submission.assignment.lesson.module.course
    if not (request.user.is_lms_admin() or course.instructor == request.user):
        messages.error(request, "Unauthorized access to this assignment submission.")
        return redirect('dashboard:instructor_assignments')
        
    if request.method == 'POST':
        try:
            marks = int(request.POST.get('marks', 0))
            feedback = request.POST.get('feedback', '').strip()
            
            max_marks = submission.assignment.max_marks
            if marks < 0 or marks > max_marks:
                messages.error(request, f"Marks must be between 0 and {max_marks}.")
                return redirect('dashboard:instructor_assignments')
                
            submission.marks_obtained = marks
            submission.feedback_text = feedback
            submission.graded = True
            submission.save()
            
            # Notify the student
            Notification.objects.create(
                user=submission.student,
                title="Assignment Graded! 📝",
                message=f"Your submission for assignment '{submission.assignment.title}' has been graded! Score: {marks}/{max_marks}."
            )
            
            messages.success(request, f"Successfully graded submission for student '{submission.student.username}'.")
        except ValueError:
            messages.error(request, "Invalid marks value submitted.")
            
    return redirect('dashboard:instructor_assignments')


# -------------------------------------------------------------
# ADMIN STUDENT FEEDBACK / REVIEWS MANAGEMENT
# -------------------------------------------------------------

@admin_required
def admin_add_feedback(request):
    """
    Admin manually adds a new student review/testimonial.
    """
    from courses.models import StudentFeedback
    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        student_role = request.POST.get('student_role_company', '').strip() or 'Student @ SJ TECH CLASSES'
        try:
            rating = int(request.POST.get('rating', 5))
        except (ValueError, TypeError):
            rating = 5
        feedback_text = request.POST.get('feedback_text', '').strip()
        is_approved = request.POST.get('is_approved') in ['on', '1', 'true', 'True', True]

        if student_name and feedback_text:
            fb = StudentFeedback(
                student_name=student_name,
                student_role_company=student_role,
                rating=min(max(1, rating), 5),
                feedback_text=feedback_text,
                is_approved=is_approved
            )
            if 'student_image' in request.FILES:
                fb.student_image = request.FILES['student_image']
            fb.save()
            messages.success(request, f"✨ Student review from '{student_name}' added successfully!")
        else:
            messages.error(request, "Student name and review comment are required.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_dashboard'))


@admin_required
def admin_update_feedback(request, feedback_id):
    """
    Admin updates an existing student feedback/review entry.
    """
    from courses.models import StudentFeedback
    feedback = get_object_or_404(StudentFeedback, id=feedback_id)

    if request.method == 'POST':
        student_name = request.POST.get('student_name', '').strip()
        student_role = request.POST.get('student_role_company', '').strip()
        try:
            rating = int(request.POST.get('rating', 5))
        except (ValueError, TypeError):
            rating = 5
        feedback_text = request.POST.get('feedback_text', '').strip()
        is_approved = request.POST.get('is_approved') in ['on', '1', 'true', 'True', True]

        if student_name:
            feedback.student_name = student_name
        if student_role:
            feedback.student_role_company = student_role
        feedback.rating = min(max(1, rating), 5)
        if feedback_text:
            feedback.feedback_text = feedback_text
        feedback.is_approved = is_approved

        if 'student_image' in request.FILES:
            feedback.student_image = request.FILES['student_image']

        feedback.save()
        messages.success(request, f"✅ Student feedback from '{feedback.student_name}' has been updated!")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_dashboard'))


@admin_required
def admin_delete_feedback(request, feedback_id):
    """
    Admin deletes a student feedback/review entry.
    """
    from courses.models import StudentFeedback
    feedback = get_object_or_404(StudentFeedback, id=feedback_id)

    if request.method == 'POST':
        name = feedback.student_name
        feedback.delete()
        messages.success(request, f"🗑️ Student review from '{name}' has been deleted.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_dashboard'))


@admin_required
def admin_toggle_feedback_approval(request, feedback_id):
    """
    1-click toggle to show or hide a student review from the home page.
    """
    from courses.models import StudentFeedback
    feedback = get_object_or_404(StudentFeedback, id=feedback_id)

    feedback.is_approved = not feedback.is_approved
    feedback.save(update_fields=['is_approved'])

    status_str = "visible on home page" if feedback.is_approved else "hidden from home page"
    messages.success(request, f"Review from '{feedback.student_name}' is now {status_str}.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:admin_dashboard'))







