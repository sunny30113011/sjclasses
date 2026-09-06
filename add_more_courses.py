import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from accounts.models import User
from courses.models import Category, Course, Module, Lesson, Quiz, QuizQuestion
from decimal import Decimal

def add_courses():
    print("Starting course creation script...")

    # Get primary instructor (Sunny Sir / Dr. Rajesh Kumar)
    instructor = User.objects.filter(role=User.ROLE_INSTRUCTOR).first()
    if not instructor:
        instructor = User.objects.filter(is_superuser=True).first()

    # Categories
    cat_fullstack, _ = Category.objects.get_or_create(name='Full Stack Development', defaults={'slug': 'full-stack-development', 'description': 'Full Stack Web Development with Python, Django, React & Node.'})
    cat_devops, _ = Category.objects.get_or_create(name='Cloud & DevOps', defaults={'slug': 'cloud-and-devops', 'description': 'AWS, Docker, Kubernetes, CI/CD, and Server Infrastructure.'})
    cat_frontend, _ = Category.objects.get_or_create(name='Frontend & UI/UX', defaults={'slug': 'frontend-and-ui-ux', 'description': 'HTML5, CSS3, Bootstrap 5, React.js, Tailwind CSS, and Figma.'})
    cat_datascience, _ = Category.objects.get_or_create(name='Data Science & AI', defaults={'slug': 'data-science-and-ai', 'description': 'Python, Machine Learning, Pandas, NumPy, and Generative AI.'})
    cat_software, _ = Category.objects.get_or_create(name='Enterprise Software', defaults={'slug': 'enterprise-software', 'description': 'Java Spring Boot, Microservices, and System Architecture.'})

    cloudinary_demo = "https://res.cloudinary.com/rydrybp7/video/upload/v1785661844/1_lfwovd.mp4"
    youtube_demo = "https://www.youtube.com/watch?v=rfscVS0vtbw"

    courses_data = [
        {
            'title': 'AWS Cloud & DevOps Engineering Bootcamp (Docker, Kubernetes & CI/CD)',
            'slug': 'aws-cloud-devops-engineering-bootcamp',
            'category': cat_devops,
            'price': Decimal('3499.00'),
            'total_duration': 45,
            'level': 'Intermediate',
            'short_description': 'Master AWS EC2/S3, Docker containerization, Kubernetes clusters, Jenkins CI/CD, and Linux administration.',
            'description': 'This comprehensive DevOps Bootcamp is designed to take you from beginner to job-ready DevOps Engineer. Learn how to deploy, scale, and manage production applications on Amazon Web Services (AWS) using industry-standard tools like Docker, Kubernetes, Terraform, and GitHub Actions.',
            'modules': [
                {
                    'title': 'Module 1: Introduction to AWS Cloud & EC2',
                    'order': 1,
                    'lessons': [
                        {'title': '1. Cloud Computing Fundamentals & AWS Architecture', 'type': 'video', 'video_url': cloudinary_demo, 'is_free': True, 'duration': 25},
                        {'title': '2. Launching & Managing EC2 Instances & Security Groups', 'type': 'video', 'video_url': youtube_demo, 'is_free': False, 'duration': 35},
                        {'title': '📄 AWS IAM & S3 Bucket Management Guide', 'type': 'pdf', 'video_url': '', 'is_free': False, 'duration': 15},
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

        {
            'title': 'Full Stack React & Node.js MERN Masterclass 2026',
            'slug': 'full-stack-react-nodejs-mern-masterclass',
            'category': cat_frontend,
            'price': Decimal('2499.00'),
            'total_duration': 50,
            'level': 'Beginner',
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

        {
            'title': 'Data Science, Machine Learning & AI with Python',
            'slug': 'data-science-machine-learning-ai-python',
            'category': cat_datascience,
            'price': Decimal('3999.00'),
            'total_duration': 60,
            'level': 'All Levels',
            'short_description': 'Complete roadmap for Data Analytics, NumPy, Pandas, Scikit-Learn, Machine Learning, and Generative AI.',
            'description': 'Unlock the power of Data Science and Artificial Intelligence. Learn how to clean data, build predictive Machine Learning models (Regression, Classification, Clustering), and integrate OpenAI & Google Gemini APIs into real applications.',
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

        {
            'title': 'Java Spring Boot 3 & Microservices Enterprise Architecture',
            'slug': 'java-spring-boot-microservices-enterprise',
            'category': cat_software,
            'price': Decimal('2999.00'),
            'total_duration': 55,
            'level': 'Intermediate',
            'short_description': 'Master Java 21, Spring Boot 3, Hibernate ORM, REST Security, Spring Cloud Eureka, and Gateway.',
            'description': 'Designed for Java developers looking to build scalable enterprise microservices. Cover Spring Data JPA, Spring Security with OAuth2/JWT, Eureka discovery server, Resilience4j circuit breakers, and Dockerized deployment.',
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

        {
            'title': 'Cybersecurity & Ethical Hacking Essentials 2026',
            'slug': 'cybersecurity-ethical-hacking-essentials',
            'category': cat_fullstack,
            'price': Decimal('1999.00'),
            'total_duration': 35,
            'level': 'Beginner',
            'short_description': 'Learn network security, penetration testing tools, OWASP Top 10 vulnerabilities, and Kali Linux.',
            'description': 'Master ethical hacking concepts and defend computer systems against cyber threats. Learn network scanning with Nmap, packet analysis with Wireshark, SQL injection mitigation, and web application security auditing.',
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
        }
    ]

    for cdata in courses_data:
        course, created = Course.objects.get_or_create(
            slug=cdata['slug'],
            defaults={
                'title': cdata['title'],
                'instructor': instructor,
                'category': cdata['category'],
                'price': cdata['price'],
                'level': cdata['level'],
                'short_description': cdata['short_description'],
                'description': cdata['description'],
                'is_published': True,
            }
        )

        if created:
            print(f"[SUCCESS] Created Course: '{course.title}'")

        # Create Modules & Lessons if not present
        for mdata in cdata.get('modules', []):
            module, _ = Module.objects.get_or_create(
                course=course,
                title=mdata['title'],
                defaults={'order': mdata['order']}
            )

            for ldata in mdata.get('lessons', []):
                Lesson.objects.get_or_create(
                    module=module,
                    title=ldata['title'],
                    defaults={
                        'lesson_type': ldata['type'],
                        'video_url': ldata['video_url'],
                        'is_free_preview': ldata['is_free'],
                        'duration_minutes': ldata['duration']
                    }
                )

            # Create Quiz if specified
            qinfo = mdata.get('quiz')
            if qinfo:
                first_lesson = module.lessons.first()
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
        else:
            print(f"[INFO] Course already exists: '{course.title}'")

    print("\n[COMPLETE] Course creation finished! Total courses in database:", Course.objects.count())

if __name__ == '__main__':
    add_courses()
