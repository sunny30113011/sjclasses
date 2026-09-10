web: python manage.py migrate && python create_admin_superuser.py && python seed_courses_and_videos.py && gunicorn lms_project.wsgi:application --bind 0.0.0.0:$PORT
