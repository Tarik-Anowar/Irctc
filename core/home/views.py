from django.shortcuts import render, redirect
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from accounts.models import User, APIKey
from home.models import *
from django.db import transaction
import logging

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


logger = logging.getLogger(__name__)

@login_required
def book_seat(request, train_number, seat_number):
    logger.info(f"Attempting to book seat {seat_number} on train {train_number} for user {request.user}")

    try:
        train = Train.objects.get(number=train_number)

        with transaction.atomic():
            seat = Seat.objects.select_for_update().get(train=train, seat_number=seat_number)

            if seat.is_booked:
                logger.warning(f"Seat {seat_number} on train {train_number} is already booked")
                return JsonResponse({"error": "Seat already booked"}, status=400)

            updated_rows = Seat.objects.filter(id=seat.id, is_booked=False).update(is_booked=True)
            
            if updated_rows == 0:
                logger.error(f"Race condition detected! Seat {seat_number} was booked just before this request.")
                return JsonResponse({"error": "Seat booking conflict, please try again"}, status=409)

            booking = Booking.objects.create(user=request.user, train=train, seat=seat)

            logger.info(f"Seat {seat_number} successfully booked for user {request.user}")
            return JsonResponse({"message": "Seat booked successfully!", "seat_number": seat_number})

    except Train.DoesNotExist:
        logger.error(f"Train {train_number} not found")
        return JsonResponse({"error": "Train not found"}, status=404)
    
    except Seat.DoesNotExist:
        logger.error(f"Seat {seat_number} not found on train {train_number}")
        return JsonResponse({"error": "Seat not found"}, status=404)
    
    except IntegrityError:
        logger.error(f"Database IntegrityError while booking seat {seat_number} on train {train_number}")
        return JsonResponse({"error": "Seat booking conflict, please try again"}, status=409)

    except Exception as e:
        logger.exception(f"Unexpected error while booking seat {seat_number}: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).select_related("train", "seat").order_by("-booked_at")

    if not bookings.exists():
        logger.info(f"No bookings found for user {request.user}")
        return render(request, "bookings.html", {"bookings": []})

    logger.info(f"User {request.user} has {bookings.count()} bookings")
    return render(request, "bookings.html", {"bookings": bookings})
