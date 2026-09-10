import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User
from courses.models import (
    Category, Course, Module, Lesson, Quiz, QuizQuestion,
    JobPlacement, PlacementRecord, ProjectFile
)
from payments.models import Coupon

def seed_all_courses():
    print("============================================================")
    print("==> SEEDING PRODUCTION COURSES & VIDEO LESSONS...")
    print("============================================================")

    # 1. Primary Instructor Account (Sunny Sir / Dr. Rajesh Kumar)
    instructor = User.objects.filter(username='sunny_admin').first()
    if not instructor:
        instructor = User.objects.filter(role=User.ROLE_INSTRUCTOR).first()
    if not instructor:
        instructor = User.objects.filter(is_superuser=True).first()
    if not instructor:
        instructor, _ = User.objects.get_or_create(
            username='instructor',
            defaults={
                'email': 'instructor@sjtechclasses.com',
                'first_name': 'Sunny',
                'last_name': 'Sir',
                'role': User.ROLE_INSTRUCTOR,
                'is_instructor_approved': True,
                'is_staff': True,
            }
        )
        instructor.set_password('SJTech@2026Admin')
        instructor.save()

    # 2. Categories
    cat_dev, _ = Category.objects.get_or_create(
        name='Web Development',
        defaults={'slug': 'web-development', 'icon': 'fa-code', 'description': 'HTML, CSS, JavaScript, React, Django & Full Stack'}
    )
    cat_fullstack, _ = Category.objects.get_or_create(
        name='Full Stack Development',
        defaults={'slug': 'full-stack-development', 'icon': 'fa-laptop-code', 'description': 'Full Stack Web Development with Python, Django, React & Node.'}
    )
    cat_devops, _ = Category.objects.get_or_create(
        name='Cloud & DevOps',
        defaults={'slug': 'cloud-and-devops', 'icon': 'fa-cloud', 'description': 'AWS, Docker, Kubernetes, CI/CD, and Server Infrastructure.'}
    )
    cat_frontend, _ = Category.objects.get_or_create(
        name='Frontend & UI/UX',
        defaults={'slug': 'frontend-and-ui-ux', 'icon': 'fa-palette', 'description': 'HTML5, CSS3, Bootstrap 5, React.js, Tailwind CSS, and Figma.'}
    )
    cat_datascience, _ = Category.objects.get_or_create(
        name='Data Science & AI',
        defaults={'slug': 'data-science-and-ai', 'icon': 'fa-brain', 'description': 'Python, Machine Learning, Deep Learning, SQL & Generative AI.'}
    )
    cat_software, _ = Category.objects.get_or_create(
        name='Enterprise Software',
        defaults={'slug': 'enterprise-software', 'icon': 'fa-cubes', 'description': 'Java Spring Boot, Microservices, and System Architecture.'}
    )
    cat_biz, _ = Category.objects.get_or_create(
        name='Business & Finance',
        defaults={'slug': 'business-and-finance', 'icon': 'fa-chart-line', 'description': 'Digital Marketing, Entrepreneurship & Freelancing.'}
    )

    # Standard CDN Video Assets
    cloudinary_demo = "https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4"
    cloudinary_template = "https://res.cloudinary.com/rydrybp7/video/upload/v1785663798/02.12.2025_20.01.51_REC_d09yhk.mp4"
    youtube_demo = "https://www.youtube.com/watch?v=rfscVS0vtbw"

    # 3. Course Definitions
    courses_data = [
        # Course 1: Master Python Django
        {
            'title': 'Master Python Django',
            'slug': 'complete-django-5-python-web-masterclass-3f3689',
            'category': cat_dev,
            'price': Decimal('2999.00'),
            'discount_price': Decimal('499.00'),
            'level': 'Beginner',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Master Python and Django 5 from scratch with real-world projects, authentication, and manual UPI payment integration.',
            'description': 'In this complete masterclass, you will build full-stack web applications using Django 5, Bootstrap 5, PostgreSQL, and custom payment engines with direct mentor support.',
            'modules': [
                {
                    'title': 'Introduction & Environment Setup',
                    'order': 1,
                    'lessons': [
                        {'title': 'Welcome & Course Overview', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 8},
                        {'title': 'Installing Python & Virtual Environment', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 12},
                    ]
                },
                {
                    'title': 'Django Models & Database',
                    'order': 2,
                    'lessons': [
                        {'title': 'Creating Models & Migrations', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': False, 'duration': 25},
                        {'title': 'Django ORM & Relationships', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': False, 'duration': 20},
                        {'title': 'Django Core Knowledge Quiz', 'type': 'quiz', 'video_url': '', 'is_free': False, 'duration': 15},
                        {'title': 'template', 'type': 'video', 'video_url': cloudinary_template, 'is_free': True, 'duration': 10},
                        {'title': 'template1', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 10},
                    ],
                    'quiz': {
                        'title': 'Django Core Knowledge Quiz',
                        'questions': [
                            {
                                'text': 'Which command is used to start a new Django application inside a project?',
                                'a': 'python manage.py startapp app_name', 'b': 'django-admin createapp app_name',
                                'c': 'python manage.py create app_name', 'd': 'django start app_name',
                                'ans': 'A', 'exp': 'django-admin startapp or python manage.py startapp is the standard command.'
                            },
                            {
                                'text': 'What is the default database engine in Django settings.py?',
                                'a': 'PostgreSQL', 'b': 'MySQL', 'c': 'SQLite3', 'd': 'MongoDB',
                                'ans': 'C', 'exp': 'SQLite3 is configured as the default database for Django projects.'
                            }
                        ]
                    }
                }
            ]
        },

        # Course 2: AWS Cloud & DevOps Engineering Bootcamp
        {
            'title': 'AWS Cloud & DevOps Engineering Bootcamp (Docker, Kubernetes & CI/CD)',
            'slug': 'aws-cloud-devops-engineering-bootcamp',
            'category': cat_devops,
            'price': Decimal('3499.00'),
            'discount_price': Decimal('3499.00'),
            'level': 'Intermediate',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Master AWS EC2/S3, Docker containerization, Kubernetes clusters, Jenkins CI/CD, and Linux administration.',
            'description': 'This comprehensive DevOps Bootcamp is designed to take you from beginner to job-ready DevOps Engineer. Learn how to deploy, scale, and manage production applications on Amazon Web Services (AWS) using industry-standard tools.',
            'modules': [
                {
                    'title': 'Module 1: Introduction to AWS Cloud & EC2',
                    'order': 1,
                    'lessons': [
                        {'title': '1. Cloud Computing Fundamentals & AWS Architecture', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 25},
                        {'title': '2. Launching & Managing EC2 Instances & Security Groups', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 35},
                        {'title': 'AWS IAM & S3 Bucket Management Guide', 'type': 'pdf', 'video_url': '', 'is_free': False, 'duration': 15},
                    ],
                    'quiz': {
                        'title': 'AWS Fundamentals & EC2 Knowledge Check',
                        'questions': [
                            {
                                'text': 'Which AWS service is used for scalable object storage?',
                                'a': 'AWS EC2', 'b': 'AWS S3', 'c': 'AWS RDS', 'd': 'AWS Lambda',
                                'ans': 'B', 'exp': 'AWS S3 (Simple Storage Service) is designed for object storage.'
                            },
                            {
                                'text': 'What component acts as a virtual firewall for EC2 instances?',
                                'a': 'Security Group', 'b': 'IAM Role', 'c': 'Route Table', 'd': 'Internet Gateway',
                                'ans': 'A', 'exp': 'Security Groups control inbound and outbound traffic for EC2.'
                            }
                        ]
                    }
                },
                {
                    'title': 'Module 2: Docker Containerization & Microservices',
                    'order': 2,
                    'lessons': [
                        {'title': '3. Understanding Docker Containers vs Virtual Machines', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 30},
                        {'title': '4. Writing Production Dockerfiles & Docker Compose Services', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 40},
                    ],
                    'quiz': {
                        'title': 'Docker & Containerization Quiz',
                        'questions': [
                            {
                                'text': 'Which command is used to build a Docker image from a Dockerfile?',
                                'a': 'docker run', 'b': 'docker build', 'c': 'docker create', 'd': 'docker image new',
                                'ans': 'B', 'exp': 'docker build creates an image from a Dockerfile.'
                            }
                        ]
                    }
                }
            ]
        },

        # Course 3: Full Stack React & Node.js MERN Masterclass 2026
        {
            'title': 'Full Stack React & Node.js MERN Masterclass 2026',
            'slug': 'full-stack-react-nodejs-mern-masterclass',
            'category': cat_frontend,
            'price': Decimal('2499.00'),
            'discount_price': Decimal('2499.00'),
            'level': 'Beginner',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Build high-performance web applications using React 19, Node.js, Express, MongoDB, and Tailwind CSS.',
            'description': 'Learn full-stack JavaScript web development from scratch! Master React hooks, Redux Toolkit state management, Node.js REST API creation, JWT authentication, and MongoDB Atlas database operations.',
            'modules': [
                {
                    'title': 'Module 1: React 19 Fundamentals & Modern Hooks',
                    'order': 1,
                    'lessons': [
                        {'title': '1. React 19 Components, JSX & State Management', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 30},
                        {'title': '2. useEffect, Custom Hooks & API Fetching', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 35},
                    ],
                    'quiz': {
                        'title': 'React Hooks & State Mastery Quiz',
                        'questions': [
                            {
                                'text': 'Which hook is used for handling side effects in React?',
                                'a': 'useState', 'b': 'useEffect', 'c': 'useContext', 'd': 'useReducer',
                                'ans': 'B', 'exp': 'useEffect is used for data fetching, subscriptions, or DOM mutations.'
                            }
                        ]
                    }
                },
                {
                    'title': 'Module 2: Node.js & Express REST API Server',
                    'order': 2,
                    'lessons': [
                        {'title': '3. Creating Express Server & Middleware Routing', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': False, 'duration': 40},
                        {'title': '4. Connecting MongoDB Mongoose Schemas & JWT Auth', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 45},
                    ]
                }
            ]
        },

        # Course 4: Data Science, Machine Learning & AI with Python
        {
            'title': 'Data Science, Machine Learning & AI with Python',
            'slug': 'data-science-machine-learning-ai-python',
            'category': cat_datascience,
            'price': Decimal('3999.00'),
            'discount_price': Decimal('3999.00'),
            'level': 'All Levels',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Complete roadmap for Data Analytics, NumPy, Pandas, Scikit-Learn, Machine Learning, and Generative AI.',
            'description': 'Unlock the power of Data Science and Artificial Intelligence. Learn how to clean data, build predictive Machine Learning models, and integrate OpenAI & Google Gemini APIs into real applications.',
            'modules': [
                {
                    'title': 'Module 1: Python Data Analysis with NumPy & Pandas',
                    'order': 1,
                    'lessons': [
                        {'title': '1. NumPy Multi-dimensional Array Manipulation', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 30},
                        {'title': '2. Pandas DataFrames, Cleaning & Data Visualization', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 40},
                    ],
                    'quiz': {
                        'title': 'Pandas & Data Processing Quiz',
                        'questions': [
                            {
                                'text': 'Which Pandas method is used to read CSV files into a DataFrame?',
                                'a': 'pd.open_csv()', 'b': 'pd.read_csv()', 'c': 'pd.load_csv()', 'd': 'pd.parse_csv()',
                                'ans': 'B', 'exp': 'pd.read_csv() imports comma-separated data into a DataFrame.'
                            }
                        ]
                    }
                }
            ]
        },

        # Course 5: Java Spring Boot 3 & Microservices Enterprise Architecture
        {
            'title': 'Java Spring Boot 3 & Microservices Enterprise Architecture',
            'slug': 'java-spring-boot-microservices-enterprise',
            'category': cat_software,
            'price': Decimal('2999.00'),
            'discount_price': Decimal('2999.00'),
            'level': 'Intermediate',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Master Java 21, Spring Boot 3, Hibernate ORM, REST Security, Spring Cloud Eureka, and Gateway.',
            'description': 'Designed for Java developers looking to build scalable enterprise microservices. Cover Spring Data JPA, Spring Security with OAuth2/JWT, Eureka discovery server, and Dockerized deployment.',
            'modules': [
                {
                    'title': 'Module 1: Spring Boot 3 Core & REST Controllers',
                    'order': 1,
                    'lessons': [
                        {'title': '1. Spring Boot 3 Initialization & Dependency Injection', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 35},
                        {'title': '2. Building RESTful APIs with Spring Data JPA & MySQL', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 45},
                    ]
                }
            ]
        },

        # Course 6: Cybersecurity & Ethical Hacking Essentials 2026
        {
            'title': 'Cybersecurity & Ethical Hacking Essentials 2026',
            'slug': 'cybersecurity-ethical-hacking-essentials',
            'category': cat_fullstack,
            'price': Decimal('1999.00'),
            'discount_price': Decimal('1999.00'),
            'level': 'Beginner',
            'preview_video_url': cloudinary_demo,
            'short_description': 'Learn network security, penetration testing tools, OWASP Top 10 vulnerabilities, and Kali Linux.',
            'description': 'Master ethical hacking concepts and defend computer systems against cyber threats. Learn network scanning with Nmap, packet analysis with Wireshark, and web application security auditing.',
            'modules': [
                {
                    'title': 'Module 1: Ethical Hacking Foundations & Kali Linux',
                    'order': 1,
                    'lessons': [
                        {'title': '1. Introduction to Ethical Hacking & Security Terms', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 25},
                        {'title': '2. Kali Linux Setup & Network Scanning with Nmap', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 35},
                    ]
                }
            ]
        },

        # Course 7: AI Engineer
        {
            'title': 'AI Engineer',
            'slug': 'ai-engineer-f7f58d',
            'category': cat_dev,
            'price': Decimal('2999.00'),
            'discount_price': Decimal('499.00'),
            'level': 'Beginner',
            'preview_video_url': 'https://youtu.be/Q9JIwtCw8AQ',
            'short_description': 'Hands-on AI Engineering Bootcamp: Prompt Engineering, LangChain, Llama, Vector Databases, and Gemini AI integration.',
            'description': 'Become a full-fledged AI Engineer. Build end-to-end intelligent apps using cutting-edge LLMs, OpenAI, Anthropic Claude, and Google Gemini APIs with production deployments.',
            'modules': [
                {
                    'title': 'Intro',
                    'order': 1,
                    'lessons': [
                        {'title': 'install', 'type': 'video', 'video_url': 'https://youtu.be/Q9JIwtCw8AQ', 'is_free': True, 'duration': 10},
                    ]
                }
            ]
        }
    ]

    # 4. Insert / Verify Courses & Lessons
    for cdata in courses_data:
        course, created = Course.objects.get_or_create(
            slug=cdata['slug'],
            defaults={
                'title': cdata['title'],
                'instructor': instructor,
                'category': cdata['category'],
                'price': cdata['price'],
                'discount_price': cdata.get('discount_price', cdata['price']),
                'level': cdata['level'],
                'preview_video_url': cdata.get('preview_video_url', ''),
                'short_description': cdata['short_description'],
                'description': cdata['description'],
                'is_published': True,
            }
        )

        status_lbl = "CREATED" if created else "VERIFIED"
        print(f"  [{status_lbl}] Course: '{course.title}'")

        for mdata in cdata.get('modules', []):
            module, _ = Module.objects.get_or_create(
                course=course,
                title=mdata['title'],
                defaults={'order': mdata['order']}
            )

            for idx, ldata in enumerate(mdata.get('lessons', []), start=1):
                lesson, l_created = Lesson.objects.get_or_create(
                    module=module,
                    title=ldata['title'],
                    defaults={
                        'lesson_type': ldata['type'],
                        'video_url': ldata['video_url'],
                        'is_free_preview': ldata['is_free'],
                        'duration_minutes': ldata['duration'],
                        'order': idx
                    }
                )
                if not l_created and not lesson.video_url and ldata['video_url']:
                    lesson.video_url = ldata['video_url']
                    lesson.save()

            qinfo = mdata.get('quiz')
            if qinfo:
                first_lesson = module.lessons.filter(lesson_type='quiz').first() or module.lessons.first()
                if first_lesson:
                    quiz, _ = Quiz.objects.get_or_create(
                        lesson=first_lesson,
                        defaults={
                            'title': qinfo['title'],
                            'pass_percentage': 70
                        }
                    )
                    for q in qinfo.get('questions', []):
                        QuizQuestion.objects.get_or_create(
                            quiz=quiz,
                            question_text=q['text'],
                            defaults={
                                'option_a': q['a'],
                                'option_b': q['b'],
                                'option_c': q['c'],
                                'option_d': q['d'],
                                'correct_option': q['ans'],
                                'explanation': q['exp']
                            }
                        )

    # 5. Seed Job Placements & Placement Records
    from datetime import date, timedelta
    if not JobPlacement.objects.exists():
        JobPlacement.objects.create(
            title="Python Full Stack Developer",
            company_name="SJ Tech Solutions",
            location="Pune / Solapur / Remote",
            job_type="Full-Time",
            salary_package="4.5 LPA - 7.5 LPA",
            skills_required="Python Django PostgreSQL HTML CSS JavaScript",
            experience_required="Freshers / 0-1 Years",
            description="We are hiring passionate Full Stack Python Developers to build web applications, REST APIs, and modern dashboards.",
            application_deadline=date.today() + timedelta(days=45)
        )
        JobPlacement.objects.create(
            title="Junior Software Engineer",
            company_name="TCS Digital",
            location="Pune / Mumbai",
            job_type="Full-Time",
            salary_package="7.0 LPA",
            skills_required="Python Data Structures SQL Git",
            experience_required="Freshers",
            description="TCS Digital is hiring entry-level software engineers proficient in Python, problem solving, and databases.",
            application_deadline=date.today() + timedelta(days=30)
        )
        print("  [CREATED] Seeded Job Placement Drives.")

    if not PlacementRecord.objects.exists():
        PlacementRecord.objects.create(student_name="Rahul Sharma", company_name="TCS Digital", package_lpa="7.00 LPA", designation="Software Engineer")
        PlacementRecord.objects.create(student_name="Priya Patel", company_name="Infosys", package_lpa="5.50 LPA", designation="Systems Engineer")
        PlacementRecord.objects.create(student_name="Amit Deshmukh", company_name="SJ Tech Solutions", package_lpa="6.20 LPA", designation="Full Stack Developer")
        print("  [CREATED] Seeded Placement Hall of Fame Records.")

    # 6. Seed Project Files
    course_obj = Course.objects.first()
    if not ProjectFile.objects.exists() and course_obj:
        import zipfile
        media_dir = os.path.join('media', 'projects')
        os.makedirs(media_dir, exist_ok=True)
        zip_path = os.path.join(media_dir, 'lms_source_code.zip')
        if not os.path.exists(zip_path):
            with zipfile.ZipFile(zip_path, 'w') as z:
                z.writestr('README.md', '# SJ TECH LMS Source Code\nRun python manage.py runserver 0.0.0.0:8000')

        ProjectFile.objects.create(
            course=course_obj,
            title="Full LMS Platform Django Source Code",
            zip_file="projects/lms_source_code.zip",
            file_size_mb=Decimal('4.50'),
            run_instructions="1. Extract zip file\n2. python -m venv venv\n3. pip install -r requirements.txt\n4. python manage.py migrate\n5. python manage.py runserver"
        )
        print("  [CREATED] Seeded Sample Project File.")

    # 7. Seed Coupons
    Coupon.objects.get_or_create(code='WELCOME20', defaults={'discount_percentage': Decimal('20.00'), 'active': True})
    Coupon.objects.get_or_create(code='FLAT50', defaults={'discount_percentage': Decimal('50.00'), 'active': True})

    total_courses = Course.objects.count()
    total_lessons = Lesson.objects.count()
    print(f"==> ALL SEEDING COMPLETE! Total Courses: {total_courses} | Total Lessons: {total_lessons}")
    print("============================================================")

if __name__ == '__main__':
    seed_all_courses()
