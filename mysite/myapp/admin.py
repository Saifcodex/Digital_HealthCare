from django.contrib import admin
from .models import *

admin.site.register(CartItem)
admin.site.register(Medicines)
admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(Doctor)
admin.site.register(DoctorTimeSlot)
admin.site.register(Appointment)