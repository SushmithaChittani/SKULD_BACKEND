# 🏋️ Skuld Backend (Fitness App)

Welcome to the Skuld Fitness App backend!  
This is a Django REST Framework project for managing workouts, challenges, user profiles, and leaderboards.

Follow these steps to set up the project from scratch after cloning.

## 🚀 Tech Stack

- Python 3.11+
- Django 5.x
- Django REST Framework
- SQLite (for local dev)
- Virtualenv
- Pip

---

📦 Setup Instructions

1. Clone the repository
git clone https://github.com/your-repo/skuld-backend.git
cd skuld-backend

2. Create virtual environment
python -m venv venv

3. Activate the virtual environment
Windows:
.\venv\Scripts\activate
Mac/linux:
source venv/bin/activate

4. Install dependencies
pip install -r requirements.txt

5. Clean previous migrations and database
del db.sqlite3
del fitness_app\migrations\*.py
python manage.py makemigrations
python manage.py migrate

6. Create superuser
python manage.py createsuperuser

7. Run the development server
python manage.py runserver
Open your browser and go to:
http://127.0.0.1:8000/

Basic project structure:
fitness_app/        # Main app
    models.py       # Database models
    views.py        # API views
    urls.py         # API endpoints
    migrations/     # DB migrations
config/             # Project config & urls
manage.py           # Django management script
requirements.txt    # Project dependencies
reset_django.bat    # Optional clean setup script for Windows



