from django.shortcuts import render
from accounts.models import User
from django.shortcuts import redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
import os
from pathlib import Path
from django.http import JsonResponse
import json

@login_required
def home(request):
    return render(request, "home.html")
