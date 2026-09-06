import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from courses.models import StudentFeedback

def seed_feedback():
    print("Seeding Student Feedback / Testimonials into database...")

    feedback_list = [
        {
            'student_name': 'Rahul Sharma',
            'student_role_company': 'Placed @ TCS Digital (7.0 LPA)',
            'rating': 5,
            'feedback_text': 'The Python Full Stack Django course by Sunny Sir is outstanding! The manual PhonePe payment process was super quick. I got my certificate and placed at TCS Digital within 2 months!'
        },
        {
            'student_name': 'Priya Patel',
            'student_role_company': 'Placed @ Infosys (5.5 LPA)',
            'rating': 5,
            'feedback_text': 'The PDF certificate generation requirement (100% lessons + passing quizzes) ensures real learning. Highly practical assignments and downloadable project source code!'
        },
        {
            'student_name': 'Amit Deshmukh',
            'student_role_company': 'Placed @ SJ Tech (6.2 LPA)',
            'rating': 5,
            'feedback_text': 'Best LMS platform in Maharashtra! Live interactive classes, online code compiler, and direct placement application links make it super easy to land software jobs.'
        },
        {
            'student_name': 'Sneha Kulkarni',
            'student_role_company': 'Placed @ Accenture (6.8 LPA)',
            'rating': 5,
            'feedback_text': 'Top Company Interview Q&A Bank helped me crack Accenture Technical round! Sample code snippets and STAR interview responses were spot on.'
        },
        {
            'student_name': 'Rohan Patil',
            'student_role_company': 'Placed @ Wipro (5.0 LPA)',
            'rating': 5,
            'feedback_text': 'Hands-on projects and source code ZIP files gave me real development experience. Sunny Sir is the best mentor for Python and Django.'
        }
    ]

    for fb in feedback_list:
        StudentFeedback.objects.get_or_create(
            student_name=fb['student_name'],
            defaults={
                'student_role_company': fb['student_role_company'],
                'rating': fb['rating'],
                'feedback_text': fb['feedback_text'],
                'is_approved': True
            }
        )

    print(f"[COMPLETE] Created {StudentFeedback.objects.count()} Student Feedback records!")

if __name__ == '__main__':
    seed_feedback()
