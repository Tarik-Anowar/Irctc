# This is a **Django-based Train Booking System**

# Installation:

# create a virtual env


python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate     # Windows


git clone https://github.com/Tarik-Anowar/Irctc.git

cd irctc
cd core
# run using docker-compose 
docker-compose up --build

# run manually
pip install -r requirements.txt

# There may be certain issue reading env varibales so replace these variables in settings.py with actual  keys 

database_url=your_database_url
secret_key=your_secret_key
debug_mode=True

# Apply migrations

python manage.py makemigrations
python manage.py migrate

# crate a super-user
python manage.py createsuperuser

# run the server
python manage.py runserver port

## Create Admin:

python manage.py shell

# run the code with in the braces 
```
    from accounts.models import User
    admin_user = User.objects.create_user(
        username="admin_user",
        email="admin@example.com",
        password="SecurePassword123",
        is_admin=True
    )

    admin_user.save()

    print(f"Admin created: {admin_user.email}, API Key: {admin_user.admin_api_key}")

```
