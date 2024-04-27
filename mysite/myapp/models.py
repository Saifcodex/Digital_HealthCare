from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.utils import timezone


# Create your models here.
# Medicine part start
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


class CartItem(models.Model):
    def __str__(self):
        return self.user.username

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accessory = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total_cost = models.IntegerField(null=True)


class Bill(models.Model):
    def __str__(self):
        return f"{self.customer.username} - {self.created_at}"

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    accessories = models.ManyToManyField(Medicines, through='BillItem')


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    accessory = models.ForeignKey(Medicines, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)


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


class DoctorTimeSlot(models.Model):
    def __str__(self):
        return f"{self.doctor.name} ({self.start_time} - {self.end_time})"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Appointment(models.Model):
    def __str__(self):
        return self.user.username

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    doctor_time_slot = models.ForeignKey(DoctorTimeSlot, on_delete=models.CASCADE)
    description = models.CharField(max_length=1000)
    appointment_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    serial_number = models.PositiveIntegerField(default=0)


# Equipment start

class Equipments(models.Model):
    def __str__(self):
        return self.e_name

    e_image = models.ImageField()
    e_name = models.CharField(max_length=100)
    e_description = models.CharField(max_length=1000)
    e_cost = models.IntegerField()
    e_count = models.IntegerField()
    vendor_name = models.CharField(max_length=100)
    vendor_description = models.CharField(max_length=100)


class CartItem1(models.Model):
    def __str__(self):
        return self.user.username

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accessory1 = models.ForeignKey(Equipments, on_delete=models.CASCADE)
    quantity1 = models.IntegerField(default=1)
    total_cost1 = models.IntegerField(null=True)

class Bill1(models.Model):
    def __str__(self):
        return f"{self.customer.username} - {self.created_at}"

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_cost1 = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    accessories1 = models.ManyToManyField(Equipments, through='BillItem1')