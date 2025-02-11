from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from accounts.models import User, APIKey
from home.models import *
from django.db import transaction


@login_required
def home(request):
    return render(request, "home.html")


@login_required
def add_train(request):
    user = request.user

    if not user.is_admin or not user.admin_api_key:
        return JsonResponse({"error": "Unauthorized access"}, status=403)

    if not APIKey.objects.filter(key=user.admin_api_key, user=user).exists():
        return JsonResponse({"error": "Invalid API key"}, status=403)

    if request.method == "POST":
        try:
            data = request.POST

            required_fields = ["train_name", "train_number", "source", "destination", "departure_time", "arrival_time", "total_seats"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                return JsonResponse({"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400)

            train = Train.objects.create(
                name=data["train_name"],
                number=data["train_number"],
                source=data["source"],
                destination=data["destination"],
                departure_time=data["departure_time"],
                arrival_time=data["arrival_time"],
                total_seats=int(data["total_seats"]),
            )
            train.save()

            return JsonResponse({"message": "Train added successfully", "train_id": train.id}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    trains = Train.objects.all()
    return render(request, "add_train.html", {"trains": trains})

@login_required
def get_trains(request):
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    if not source or not destination:
        return JsonResponse({"error": "Missing source or destination"}, status=400)
    trains = Train.objects.filter(source=source, destination=destination).values(
        "id", "name", "number", "departure_time", "arrival_time"
    )
    return JsonResponse(list(trains), safe=False)

@login_required
def get_seats(request, train_number):  
    try:
        print(train_number)
        train = Train.objects.filter(number=train_number).first()
        print(train)
        seats = Seat.objects.filter(train=train).values("id", "seat_number", "is_booked")
        seat_list = list(seats)
        return JsonResponse(seat_list, safe=False)

    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def book_seat(request, train_number, seat_number):
    print("Train Number:", train_number)
    print("Seat Number:", seat_number)

    try:
        # Fetch train correctly
        train = Train.objects.filter(number=train_number).first()
        if not train:
            return JsonResponse({"error": "Train not found"}, status=404)

        # Use transaction to prevent race conditions
        with transaction.atomic():
            # Lock the seat row for update
            seat = Seat.objects.select_for_update().filter(train=train, seat_number=seat_number).first()
            if not seat:
                return JsonResponse({"error": "Seat not found"}, status=404)

            if seat.is_booked:
                return JsonResponse({"error": "Seat already booked"}, status=400)

            # Create booking
            booking = Booking.objects.create(user=request.user, train=train, seat=seat)

            # Mark seat as booked
            seat.is_booked = True
            seat.save()

            return JsonResponse({"message": "Seat booked successfully!", "seat_number": seat_number})

    except Exception as e:
        print("Booking error:", e)
        return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("train", "seat").order_by("-booked_at")
    print(bookings[0])
    return render(request, "bookings.html", {"bookings": bookings})