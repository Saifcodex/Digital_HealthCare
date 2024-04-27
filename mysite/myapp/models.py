from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils import timezone

# Create your models here.
class Medicines(models.Model):
    def __str__(self):
        return self.p_name

    p_image = models.ImageField()
    p_name = models.CharField(max_length=100)
    p_description = models.CharField(max_length=1000)
    p_cost = models.IntegerField()
    p_count = models.IntegerField()
    v_name = models.CharField(max_length=100)
    v_description = models.CharField(max_length=100)


# doctor modal started
class Doctor(models.Model):
    def __str__(self):
        return self.name

    image = models.ImageField()
    name = models.CharField(max_length=255)
    specialty = models.CharField(max_length=255)
    status = models.BooleanField(default=True)
    cost = models.IntegerField()
    available_spots = models.PositiveIntegerField()
    next_available_appointment_date = models.DateField(null=True, blank=True)
