from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError

class Train(models.Model):
    id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=100, unique=True)
    number = models.CharField(max_length=20, unique=True) 
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    total_seats = models.PositiveIntegerField(default=0)  

    def __str__(self):
        return f"{self.name} ({self.source} → {self.destination}): {self.departure_time}"

class Seat(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="seats") 
    seat_number = models.PositiveIntegerField()  
    is_booked = models.BooleanField(default=False)  

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['train', 'seat_number'], name="unique_train_seat")
        ]

    def __str__(self):
        return f"Seat {self.seat_number} - {self.train.name} ({'Booked' if self.is_booked else 'Available'})"

@receiver(post_save, sender=Train)
def create_train_seats(sender, instance, created, **kwargs):
    if created and instance.total_seats > 0:
        seats = [Seat(train=instance, seat_number=i+1) for i in range(instance.total_seats)]
        Seat.objects.bulk_create(seats)

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.seat.is_booked:
            raise ValidationError(f"Seat {self.seat.seat_number} is already booked!")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking by {self.user.email} - Seat {self.seat.seat_number} on {self.train.name}"

@receiver(post_save, sender=Booking)
def mark_seat_as_booked(sender, instance, created, **kwargs):
    if created:
        instance.seat.is_booked = True
        instance.seat.save()
