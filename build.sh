#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "==> Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Collecting static files..."
python manage.py collectstatic --no-input

echo "==> Applying database migrations..."
python manage.py migrate

echo "==> Ensuring initial superuser exists..."
python create_admin_superuser.py

echo "==> Seeding initial reviews, interview questions & carousel slides..."
python seed_student_feedback.py
python seed_interview_questions.py
python seed_carousel_slides.py

echo "==> Seeding production courses, video lessons, modules & projects..."
python seed_courses_and_videos.py

echo "==> Build completed successfully!"


