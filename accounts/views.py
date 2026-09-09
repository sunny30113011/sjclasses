from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentRegistrationForm, InstructorRegistrationForm, UserProfileForm
from django.contrib.auth.forms import AuthenticationForm
from .emails import send_welcome_email, send_password_reset_otp_email, generate_otp

User = get_user_model()

def register_student(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')
    
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password')
            user = form.save()
            login(request, user, backend='accounts.backends.EmailOrUsernameBackend')
            request.session['welcome_credentials'] = {
                'username': user.username,
                'password': raw_password,
                'email': user.email,
            }
            try:
                send_welcome_email(user, raw_password=raw_password)
            except Exception:
                pass
            messages.success(request, f"Welcome to SJ TECH CLASSES, {user.username}! Your student account has been created.")
            return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, "Please check the form for errors below.")
    else:
        form = StudentRegistrationForm()
    return render(request, 'accounts/register_student.html', {'form': form})


def register_instructor(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = InstructorRegistrationForm(request.POST)
        if form.is_valid():
            raw_password = form.cleaned_data.get('password')
            user = form.save()
            login(request, user, backend='accounts.backends.EmailOrUsernameBackend')
            request.session['welcome_credentials'] = {
                'username': user.username,
                'password': raw_password,
                'email': user.email,
            }
            try:
                send_welcome_email(user, raw_password=raw_password)
            except Exception:
                pass
            messages.success(request, f"Welcome {user.username}! Your instructor application has been submitted for Admin approval.")
            return redirect('accounts:instructor_pending_approval')
        else:
            messages.error(request, "Please check the form for errors below.")
    else:
        form = InstructorRegistrationForm()
    return render(request, 'accounts/register_instructor.html', {'form': form})



@login_required
def instructor_pending_approval(request):
    """
    Status view for instructors awaiting administrator approval.
    """
    if request.user.is_instructor() or request.user.is_lms_admin():
        return redirect('dashboard:instructor_dashboard')

    if not request.user.is_pending_instructor():
        return redirect('dashboard:student_dashboard')

    welcome_creds = request.session.pop('welcome_credentials', None)
    return render(request, 'accounts/instructor_pending_approval.html', {
        'instructor': request.user,
        'welcome_creds': welcome_creds
    })


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('courses:home')


@login_required
def user_profile(request):
    show_form = request.GET.get('edit') == '1'
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully!")
            return redirect('accounts:profile')
        else:
            show_form = True
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'accounts/profile.html', {
        'form': form,
        'show_form': show_form
    })


def instructor_profile(request, username):
    from courses.models import Course, Enrollment
    instructor = get_object_or_404(User, username=username, role=User.ROLE_INSTRUCTOR)
    courses = Course.objects.filter(instructor=instructor, is_published=True)
    total_students = Enrollment.objects.filter(course__instructor=instructor).count()
    return render(request, 'accounts/instructor_profile.html', {
        'instructor': instructor,
        'courses': courses,
        'total_students': total_students,
    })


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        user = User.objects.filter(email=email).first()
        if user:
            otp_code = generate_otp()
            request.session['reset_otp'] = otp_code
            request.session['reset_user_id'] = user.id
            send_password_reset_otp_email(user, otp_code)
            messages.success(request, f"A 6-digit OTP code has been sent to {user.email}.")
            return redirect('accounts:verify_otp')
        else:
            messages.error(request, "No account found with this email address.")
    return render(request, 'accounts/forgot_password.html')


def verify_otp(request):
    if request.method == 'POST':
        otp = request.POST.get('otp', '').strip()
        new_password = request.POST.get('new_password', '').strip()
        stored_otp = request.session.get('reset_otp')
        user_id = request.session.get('reset_user_id')

        if stored_otp and user_id and otp == stored_otp:
            user = get_object_or_404(User, id=user_id)
            user.set_password(new_password)
            user.save()
            login(request, user)
            del request.session['reset_otp']
            del request.session['reset_user_id']
            messages.success(request, "🎉 Your password has been reset successfully!")
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, "Invalid or expired OTP code.")
    return render(request, 'accounts/verify_otp.html')
