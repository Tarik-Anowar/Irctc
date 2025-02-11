from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Train(models.Model):
    id = models.AutoField(primary_key=True)  
    name = models.CharField(max_length=100, unique=True)
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
        primary_key = ('train', 'seat_number')  

    def __str__(self):
        return f"Seat {self.seat_number} - {self.train.name} ({'Booked' if self.is_booked else 'Available'})"


@receiver(post_save, sender=Train)
def create_train_seats(sender, instance, created, **kwargs):
    if created and instance.total_seats > 0:
        seats = [Seat(train=instance, seat_number=i+1) for i in range(instance.total_seats)]
        Seat.objects.bulk_create(seats) 
