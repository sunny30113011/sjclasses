import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lms_project.settings')
django.setup()

from courses.models import CarouselSlide

def seed_carousel():
    print("Seeding Carousel Slides into database...")

    slides_data = [
        {
            'title': 'Learn Today,',
            'highlight_text': 'Build Tomorrow',
            'badge_text': 'SJ TECH CLASSES',
            'badge_icon': 'fa-rocket',
            'description': 'Master Full Stack Web Development, Python, Django, Databases, and AI. Get certified with official ReportLab PDF credentials.',
            'online_image_url': '/static/images/hero1.jpg',
            'primary_btn_text': 'Explore All Courses',
            'primary_btn_url': '/courses/',
            'secondary_btn_text': 'Placement Drive',
            'secondary_btn_url': '/placements/',
            'gradient_css': 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)',
            'order': 1,
            'is_active': True,
        },
        {
            'title': 'Pay via',
            'highlight_text': 'PhonePe, GPay, Paytm',
            'badge_text': 'Easy Manual Payment',
            'badge_icon': 'fa-qrcode',
            'description': 'No Razorpay extra fees! Scan QR Code, enter your 12-digit UTR number & payment screenshot. Fast admin approval unlocks course instantly!',
            'online_image_url': '/static/images/hero2.jpg',
            'primary_btn_text': 'Buy Course Now',
            'primary_btn_url': '/courses/',
            'secondary_btn_text': '',
            'secondary_btn_url': '',
            'gradient_css': 'linear-gradient(135deg, #065f46 0%, #047857 100%)',
            'order': 2,
            'is_active': True,
        },
        {
            'title': 'Guaranteed',
            'highlight_text': 'Placement Support',
            'badge_text': '100+ Hiring Partners',
            'badge_icon': 'fa-briefcase',
            'description': 'Direct hiring drives with top MNCs & IT startups. 95% placement rate with packages up to 12 LPA.',
            'online_image_url': '/static/images/hero3.jpg',
            'primary_btn_text': 'View Active Job Drives',
            'primary_btn_url': '/placements/',
            'secondary_btn_text': '',
            'secondary_btn_url': '',
            'gradient_css': 'linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)',
            'order': 3,
            'is_active': True,
        },
        {
            'title': 'In-Browser',
            'highlight_text': 'Code Compiler',
            'badge_text': 'Online Coding Sandbox',
            'badge_icon': 'fa-code',
            'description': 'Write and run Python 3, JavaScript, and HTML/CSS live code directly inside your browser without installing local software.',
            'online_image_url': '/static/images/hero1.jpg',
            'primary_btn_text': 'Try Code Compiler',
            'primary_btn_url': '/compiler/',
            'secondary_btn_text': '',
            'secondary_btn_url': '',
            'gradient_css': 'linear-gradient(135deg, #4c1d95 0%, #7c3aed 100%)',
            'order': 4,
            'is_active': True,
        }
    ]

    for slide in slides_data:
        obj, created = CarouselSlide.objects.get_or_create(
            order=slide['order'],
            defaults=slide
        )
        if created:
            print(f"  [+] Created slide {obj.order}: {obj.title} {obj.highlight_text}")
        else:
            print(f"  [.] Slide {obj.order} already exists")

    print("Seeding Carousel Slides completed successfully!")

if __name__ == '__main__':
    seed_carousel()
