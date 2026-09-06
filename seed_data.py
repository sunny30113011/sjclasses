import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User
from courses.models import Category, Course, Module, Lesson, Quiz, QuizQuestion
from payments.models import Coupon

def seed():
    print("Seeding database initial records...")

    # 1. Professional Admin Accounts (5 Production Credentials)
    admin_accounts = [
        {
            'username': 'sjadmin',
            'password': 'SJTech@2026Admin',
            'email': 'sunnywaghmode8@gmail.com',
            'first_name': 'Sunny',
            'last_name': 'Sir (Founder)',
        },
        {
            'username': 'lms_admin',
            'password': 'SJTech@LmsMaster2026',
            'email': 'admin@sjtechclasses.com',
            'first_name': 'LMS Master',
            'last_name': 'Admin',
        },
        {
            'username': 'sysadmin',
            'password': 'SysAdmin#SJTech2026',
            'email': 'sysadmin@sjtechclasses.com',
            'first_name': 'Systems',
            'last_name': 'Lead Controller',
        },
        {
            'username': 'super_admin',
            'password': 'SuperAdmin!SJTech2026',
            'email': 'cto@sjtechclasses.com',
            'first_name': 'Chief Technical',
            'last_name': 'Officer',
        },
        {
            'username': 'hiring_admin',
            'password': 'HiringAdmin@SJTech2026',
            'email': 'placements@sjtechclasses.com',
            'first_name': 'Head of',
            'last_name': 'Placements & Operations',
        },
        {
            'username': 'admin',
            'password': 'admin123',
            'email': 'admin@edulearn.com',
            'first_name': 'System',
            'last_name': 'Admin',
        }
    ]

    for acc in admin_accounts:
        adm, created = User.objects.get_or_create(
            username=acc['username'],
            defaults={
                'email': acc['email'],
                'first_name': acc['first_name'],
                'last_name': acc['last_name'],
                'role': User.ROLE_ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created or not adm.check_password(acc['password']):
            adm.set_password(acc['password'])
            adm.role = User.ROLE_ADMIN
            adm.is_staff = True
            adm.is_superuser = True
            adm.save()
            print(f"Configured Admin Account: {acc['username']} / {acc['password']}")


    # 2. Instructor account
    instructor, created = User.objects.get_or_create(
        username='instructor',
        defaults={
            'email': 'instructor@edulearn.com',
            'first_name': 'Dr. Rajesh',
            'last_name': 'Kumar',
            'headline': 'Senior Full Stack & AI Architect',
            'role': User.ROLE_INSTRUCTOR,
            'upi_id': 'instructor@upi'
        }
    )
    if created:
        instructor.set_password('instructor123')
        instructor.save()
        print("Created Instructor (instructor / instructor123)")

    # 3. Student account
    student, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@edulearn.com',
            'first_name': 'Rahul',
            'last_name': 'Sharma',
            'role': User.ROLE_STUDENT,
        }
    )
    if created:
        student.set_password('student123')
        student.save()
        print("Created Student (student / student123)")

    # 4. Categories
    cat_dev, _ = Category.objects.get_or_create(name='Web Development', icon='fa-code', description='HTML, CSS, JavaScript, React, Django & Full Stack')
    cat_ds, _ = Category.objects.get_or_create(name='Data Science & AI', icon='fa-brain', description='Python, Machine Learning, Deep Learning & SQL')
    cat_design, _ = Category.objects.get_or_create(name='UI/UX & Design', icon='fa-palette', description='Figma, Web Design & Design Systems')
    cat_biz, _ = Category.objects.get_or_create(name='Business & Finance', icon='fa-chart-line', description='Digital Marketing, Entrepreneurship & Stocks')

    # 5. Sample Courses
    c1, created = Course.objects.get_or_create(
        title='Complete Django 5 & Python Web Masterclass',
        defaults={
            'instructor': instructor,
            'category': cat_dev,
            'short_description': 'Master Django 5 from scratch with real-world projects, authentication, and manual UPI payment integration.',
            'description': 'In this complete masterclass, you will build full-stack web applications using Django 5, Bootstrap 5, PostgreSQL, and custom payment engines.',
            'price': 2999.00,
            'discount_price': 499.00,
            'level': 'Beginner',
            'preview_video_url': 'https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4',
            'is_published': True
        }
    )

    if created:
        # Modules & Lessons for c1
        m1 = Module.objects.create(course=c1, title='Introduction & Environment Setup', order=1)
        l1 = Lesson.objects.create(
            module=m1, title='Welcome & Course Overview', lesson_type='video',
            video_url='https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4', duration_minutes=8, order=1, is_free_preview=True
        )
        l2 = Lesson.objects.create(
            module=m1, title='Installing Python & Virtual Environment', lesson_type='video',
            video_url='https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4', duration_minutes=12, order=2, is_free_preview=True
        )

        m2 = Module.objects.create(course=c1, title='Django Models & Database', order=2)
        l3 = Lesson.objects.create(
            module=m2, title='Creating Models & Migrations', lesson_type='video',
            video_url='https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4', duration_minutes=25, order=1
        )
        l4 = Lesson.objects.create(
            module=m2, title='Django ORM & Relationships', lesson_type='video',
            video_url='https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4', duration_minutes=20, order=2
        )



        # MCQ Quiz Lesson
        l5 = Lesson.objects.create(
            module=m2, title='Django Core Knowledge Quiz', lesson_type='quiz', duration_minutes=15, order=3
        )
        quiz = Quiz.objects.create(lesson=l5, title='Django Core Assessment Quiz', pass_percentage=60)
        
        QuizQuestion.objects.create(
            quiz=quiz,
            question_text='Which command is used to start a new Django application inside a project?',
            option_a='python manage.py startapp app_name',
            option_b='django-admin createapp app_name',
            option_c='python manage.py create app_name',
            option_d='django start app_name',
            correct_option='A',
            explanation='django-admin startapp or python manage.py startapp is the standard command.'
        )

        QuizQuestion.objects.create(
            quiz=quiz,
            question_text='What is the default database engine in Django settings.py?',
            option_a='PostgreSQL',
            option_b='MySQL',
            option_c='SQLite3',
            option_d='MongoDB',
            correct_option='C',
            explanation='SQLite3 is configured as the default database for Django projects.'
        )

    # 6. Sample Coupon
    Coupon.objects.get_or_create(code='WELCOME20', discount_percentage=20.00, active=True)
    Coupon.objects.get_or_create(code='FLAT50', discount_percentage=50.00, active=True)

    # Seed Placement Data
    from courses.models import JobPlacement, PlacementRecord
    from datetime import date, timedelta

    if not JobPlacement.objects.exists():
        j1 = JobPlacement.objects.create(
            title="Python Full Stack Developer",
            company_name="SJ Tech Solutions",
            location="Pune / Remote",
            job_type="Full-Time",
            salary_package="4.5 LPA - 7.5 LPA",
            skills_required="Python Django PostgreSQL HTML CSS JavaScript",
            experience_required="Freshers / 0-1 Years",
            description="We are hiring passionate Full Stack Python Developers to build web applications, REST APIs, and modern dashboards.",
            application_deadline=date.today() + timedelta(days=30)
        )
        j2 = JobPlacement.objects.create(
            title="Junior Software Engineer",
            company_name="TCS Digital",
            location="Pune / Mumbai",
            job_type="Full-Time",
            salary_package="7.0 LPA",
            skills_required="Python Data Structures SQL Git",
            experience_required="Freshers",
            description="TCS Digital is hiring entry-level software engineers proficient in Python, problem solving, and databases.",
            application_deadline=date.today() + timedelta(days=20)
        )
        print("Seeded Job Placement Drives.")

    if not PlacementRecord.objects.exists():
        PlacementRecord.objects.create(student_name="Rahul Sharma", company_name="TCS Digital", package_lpa=7.00, designation="Software Engineer")
        PlacementRecord.objects.create(student_name="Priya Patel", company_name="Infosys", package_lpa=5.50, designation="Systems Engineer")
        PlacementRecord.objects.create(student_name="Amit Deshmukh", company_name="SJ Tech Solutions", package_lpa=6.20, designation="Full Stack Developer")
        print("Seeded Placement Hall of Fame Records.")

    # Seed Project Files
    from courses.models import ProjectFile
    import os, zipfile
    course_obj = Course.objects.first()
    if not ProjectFile.objects.exists() and course_obj:
        media_dir = os.path.join('media', 'projects')
        os.makedirs(media_dir, exist_ok=True)
        zip_path = os.path.join(media_dir, 'lms_source_code.zip')
        if not os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'w') as z:
                z.writestr('README.md', '# SJ TECH LMS Source Code\nRun python manage.py runserver 0.0.0.0:8000')

        pf = ProjectFile.objects.create(
            course=course_obj,
            title="Full LMS Platform Django Source Code",
            zip_file="projects/lms_source_code.zip",
            file_size_mb=4.50,
            run_instructions="""1. Extract the downloaded project .ZIP archive.
2. Open terminal inside directory: cd finalSj
3. Create virtual environment: python -m venv venv
4. Activate venv: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)
5. Install dependencies: pip install django pillow reportlab qrcode
6. Run migrations: python manage.py migrate
7. Start dev server: python manage.py runserver 0.0.0.0:8000"""
        )
        print("Seeded Sample Project File.")

    print("\nDatabase seeded successfully!")




if __name__ == '__main__':
    seed()
