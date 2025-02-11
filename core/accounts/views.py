from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password
from accounts.models import User
from django.core.exceptions import ValidationError
from django.contrib import messages

def signup(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not name or not email or not password:
            messages.error(request, "All fields are required.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect("signup")

        try:
            hashed_password = make_password(password)

            user = User.objects.create(
                username=name,  
                email=email,
                password=hashed_password,
            )
            user.save()

            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect("signup")

    return render(request, "signup.html")
def signin(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = User.objects.filter(email=email).first()
        
        if user is None:
            messages.error(request, "No user found with this email. Please try again or register.")
            return redirect("signin")

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect("signin")

    return render(request, "signin.html")
