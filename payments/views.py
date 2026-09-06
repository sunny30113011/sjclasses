from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, Coupon, Payment, AllAccessPlan
from courses.models import Course, Enrollment, Notification

@login_required
def cart_detail(request):
    cart_items = Cart.objects.filter(user=request.user).select_related('course')
    subtotal = sum(item.course.discount_price for item in cart_items)
    
    # Coupon calculation
    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id, active=True).first()
        if coupon:
            discount_amount = (subtotal * coupon.discount_percentage) / 100

    total_amount = max(0, subtotal - discount_amount)

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'coupon': coupon,
    }
    return render(request, 'payments/cart.html', context)


@login_required
def add_to_cart(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, "You are already enrolled in this course.")
        return redirect('courses:lesson_player', course_slug=course.slug)

    Cart.objects.get_or_create(user=request.user, course=course)
    messages.success(request, f"Added '{course.title}' to your cart.")
    return redirect('payments:cart_detail')


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    messages.info(request, "Item removed from cart.")
    return redirect('payments:cart_detail')


@login_required
def apply_coupon(request):
    if request.method == 'POST':
        code = request.POST.get('coupon_code', '').strip()
        coupon = Coupon.objects.filter(code__iexact=code, active=True).first()
        if coupon:
            request.session['coupon_id'] = coupon.id
            messages.success(request, f"Coupon '{coupon.code}' applied! Saved {coupon.discount_percentage}%.")
        else:
            messages.error(request, "Invalid or expired coupon code.")
    return redirect('payments:cart_detail')


@login_required
def checkout(request, course_id=None):
    if course_id:
        course = get_object_or_404(Course, id=course_id)
        courses_to_buy = [course]
        subtotal = course.discount_price
    else:
        cart_items = Cart.objects.filter(user=request.user).select_related('course')
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect('courses:course_list')
        courses_to_buy = [item.course for item in cart_items]
        subtotal = sum(c.discount_price for c in courses_to_buy)

    coupon_id = request.session.get('coupon_id')
    discount_amount = 0
    coupon = None
    if coupon_id:
        coupon = Coupon.objects.filter(id=coupon_id, active=True).first()
        if coupon:
            discount_amount = (subtotal * coupon.discount_percentage) / 100

    total_amount = max(0, subtotal - discount_amount)

    plan = AllAccessPlan.get_active_plan()
    upi_id = plan.upi_id if plan and plan.upi_id else "sunnywaghmode8@axl"
    upi_number = plan.upi_number if plan and plan.upi_number else "7218858764"

    context = {
        'courses_to_buy': courses_to_buy,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'total_amount': total_amount,
        'coupon': coupon,
        'upi_id': upi_id,
        'upi_number': upi_number,
        'single_course_id': course_id,
    }
    return render(request, 'payments/checkout.html', context)


from accounts.emails import send_payment_received_email

from .validators import validate_image_file

@login_required
def submit_manual_payment(request):
    if request.method == 'POST':
        utr = request.POST.get('utr', '').strip()
        screenshot = request.FILES.get('screenshot')
        course_id = request.POST.get('course_id')

        if not utr or len(utr) < 6:
            messages.error(request, "Please enter a valid UTR / Transaction Reference ID.")
            return redirect(request.META.get('HTTP_REFERER', 'payments:cart_detail'))

        # Security 1: Duplicate UTR Detection
        if Payment.objects.filter(utr__iexact=utr).exists():
            messages.error(request, f"🔒 Duplicate UTR Error: Transaction ID '{utr}' has already been submitted or processed. Please double check your UTR number.")
            return redirect(request.META.get('HTTP_REFERER', 'payments:cart_detail'))

        if not screenshot:
            messages.error(request, "Please upload your payment screenshot receipt.")
            return redirect(request.META.get('HTTP_REFERER', 'payments:cart_detail'))

        # Security 2: Image Type & File Size Validation
        is_valid_img, img_err = validate_image_file(screenshot, max_size_mb=5)
        if not is_valid_img:
            messages.error(request, f"🔒 Receipt Upload Error: {img_err}")
            return redirect(request.META.get('HTTP_REFERER', 'payments:cart_detail'))

        if course_id:
            courses = [get_object_or_404(Course, id=course_id)]
        else:
            cart_items = Cart.objects.filter(user=request.user).select_related('course')
            courses = [item.course for item in cart_items]


        coupon_id = request.session.get('coupon_id')
        coupon = Coupon.objects.filter(id=coupon_id).first() if coupon_id else None

        for course in courses:
            subtotal = course.discount_price
            discount = (subtotal * coupon.discount_percentage / 100) if coupon else 0
            final_amt = max(0, subtotal - discount)

            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=final_amt,
                utr=utr,
                screenshot=screenshot,
                payment_status='Pending'
            )
            # Send Email Notification
            send_payment_received_email(payment)


        if not course_id:
            Cart.objects.filter(user=request.user).delete()
        
        if 'coupon_id' in request.session:
            del request.session['coupon_id']

        Notification.objects.create(
            user=request.user,
            title="Payment Submitted 📲",
            message=f"Your payment with UTR {utr} is pending admin approval. Course access will unlock once verified."
        )

        messages.success(request, f"🎉 Payment submitted successfully! UTR: {utr}. Admin will verify and unlock your course shortly.")
        return redirect('payments:payment_success')

    return redirect('payments:cart_detail')


@login_required
def checkout_project(request, project_id):
    from courses.models import ProjectFile, ProjectPurchase
    project = get_object_or_404(ProjectFile, id=project_id)
    
    # Check if already purchased & approved
    existing = ProjectPurchase.objects.filter(student=request.user, project=project, is_approved=True).first()
    if existing:
        messages.info(request, f"You have already unlocked '{project.title}'. You can download the source code anytime!")
        return redirect('courses:projects_portal')

    pending_purchase = ProjectPurchase.objects.filter(student=request.user, project=project, is_approved=False).first()

    plan = AllAccessPlan.get_active_plan()
    upi_id = plan.upi_id if plan and plan.upi_id else "sunnywaghmode8@axl"
    upi_number = plan.upi_number if plan and plan.upi_number else "7218858764"

    context = {
        'project': project,
        'amount': project.price,
        'upi_id': upi_id,
        'upi_number': upi_number,
        'pending_purchase': pending_purchase,
    }
    return render(request, 'payments/checkout_project.html', context)


@login_required
def submit_project_payment(request):
    if request.method == 'POST':
        from courses.models import ProjectFile, ProjectPurchase
        project_id = request.POST.get('project_id')
        utr = request.POST.get('utr', '').strip()
        screenshot = request.FILES.get('screenshot')

        project = get_object_or_404(ProjectFile, id=project_id)

        if not utr or len(utr) < 6:
            messages.error(request, "Please enter a valid 12-digit UTR / Transaction Reference ID.")
            return redirect('payments:checkout_project', project_id=project.id)

        if Payment.objects.filter(utr__iexact=utr).exists():
            messages.error(request, f"🔒 Duplicate UTR Error: Transaction ID '{utr}' has already been submitted or processed.")
            return redirect('payments:checkout_project', project_id=project.id)

        if not screenshot:
            messages.error(request, "Please upload your PhonePe/UPI payment receipt screenshot.")
            return redirect('payments:checkout_project', project_id=project.id)

        is_valid_img, img_err = validate_image_file(screenshot, max_size_mb=5)
        if not is_valid_img:
            messages.error(request, f"🔒 Upload Error: {img_err}")
            return redirect('payments:checkout_project', project_id=project.id)

        payment = Payment.objects.create(
            user=request.user,
            course=project.course if project.course else None,
            amount=project.price,
            utr=utr,
            screenshot=screenshot,
            payment_status='Pending'
        )

        ProjectPurchase.objects.update_or_create(
            student=request.user,
            project=project,
            defaults={'payment': payment, 'is_approved': False}
        )

        send_payment_received_email(payment)

        Notification.objects.create(
            user=request.user,
            title="Project Payment Submitted 📲",
            message=f"Your payment of ₹{project.price} for project '{project.title}' (UTR: {utr}) is pending admin verification."
        )

        messages.success(request, f"🎉 Payment submitted successfully! UTR: {utr}. Admin will verify and unlock your .ZIP download shortly.")
        return redirect('payments:payment_success')

    return redirect('courses:projects_portal')


@login_required
def payment_success(request):
    return render(request, 'payments/payment_success.html')


def all_access_checkout(request):
    """
    Landing and checkout page for unlocking ALL courses for a single price.
    """
    plan = AllAccessPlan.get_active_plan()
    if not plan:
        messages.info(request, "The All-Access Pass offer is currently unavailable.")
        return redirect('courses:course_list')

    published_courses = Course.objects.filter(is_published=True).select_related('instructor', 'category')
    total_individual_val = sum(c.price for c in published_courses) or 9999
    
    already_unlocked = False
    is_expired_all_access = False
    pending_payment = None

    if request.user.is_authenticated:
        already_unlocked = hasattr(request.user, 'is_all_access_valid') and request.user.is_all_access_valid()
        is_expired_all_access = getattr(request.user, 'has_all_access', False) and not already_unlocked
        pending_payment = Payment.objects.filter(
            user=request.user, 
            is_all_access=True, 
            payment_status='Pending'
        ).first()

    context = {
        'plan': plan,
        'published_courses': published_courses,
        'total_individual_val': total_individual_val,
        'already_unlocked': already_unlocked,
        'is_expired_all_access': is_expired_all_access,
        'pending_payment': pending_payment,
        'features': plan.get_features_list(),
    }
    return render(request, 'payments/all_access_checkout.html', context)


@login_required
def submit_all_access_payment(request):
    """
    Process manual UPI payment submission for the All-Access Pass.
    """
    if request.method == 'POST':
        plan = AllAccessPlan.get_active_plan()
        if not plan:
            messages.error(request, "The All-Access Pass offer is currently closed.")
            return redirect('courses:course_list')

        utr = request.POST.get('utr', '').strip()
        screenshot = request.FILES.get('screenshot')

        if not utr or len(utr) < 6:
            messages.error(request, "Please enter a valid 12-digit UTR / Transaction Reference ID.")
            return redirect('payments:all_access_checkout')

        # Check duplicate UTR
        if Payment.objects.filter(utr__iexact=utr).exists():
            messages.error(request, f"🔒 Duplicate UTR Error: Transaction ID '{utr}' has already been submitted or processed.")
            return redirect('payments:all_access_checkout')

        if not screenshot:
            messages.error(request, "Please upload your PhonePe/GooglePay/UPI payment screenshot.")
            return redirect('payments:all_access_checkout')

        is_valid_img, img_err = validate_image_file(screenshot, max_size_mb=5)
        if not is_valid_img:
            messages.error(request, f"🔒 Receipt Upload Error: {img_err}")
            return redirect('payments:all_access_checkout')

        # Create payment record for All-Access
        payment = Payment.objects.create(
            user=request.user,
            course=None,
            is_all_access=True,
            amount=plan.offer_price,
            utr=utr,
            screenshot=screenshot,
            payment_status='Pending'
        )

        try:
            send_payment_received_email(payment)
        except Exception:
            pass

        Notification.objects.create(
            user=request.user,
            title="All-Access Pass Payment Submitted 📲",
            message=f"Your payment of ₹{plan.offer_price} for All-Access VIP Pass (UTR: {utr}) is pending admin verification. All courses will unlock upon approval!",
            notification_type='offer',
            link='/payment/all-access/'
        )

        messages.success(request, f"🎉 All-Access payment submitted successfully! UTR: {utr}. Admin will verify and unlock all courses shortly.")
        return redirect('payments:payment_success')

    return redirect('payments:all_access_checkout')


