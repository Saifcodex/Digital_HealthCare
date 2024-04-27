from django.utils import timezone
from django.urls import reverse
from django.db.models import Prefetch
from .models import *
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import (
    authenticate,
    login as auth_login,
    logout as auth_logout
)
from .forms import Captcha, UserProfileForm, UserForm
from django.db.models import Q


# Shift kora function

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    return render(request, 'contact.html')


def FAQ(request):
    return render(request, 'FAQ.html')


# doctor function started

def doctors(request):
    doctors = Doctor.objects.all()
    context = {
        'doctors': doctors
    }
    return render(request, "doctors.html", context)


def doctor_search(request):
    query_d = request.GET.get('q')

    if query_d:
        words = query_d.split()
        name_query = Q()
        specialty_query = Q()
        status_query = Q()

        for word in words:
            if word.lower() == "available":
                status_query = Q(status=True)

            elif word.lower() == "unavailable":
                status_query = Q(status=False)

            else:
                name_query |= Q(name__icontains=word)
                specialty_query |= Q(specialty__icontains=word)

        doctors = Doctor.objects.filter(name_query | specialty_query, status_query)
    else:
        messages.error(request, "Search bar was empty")
        return redirect('doctors')

    if not doctors:
        messages.error(request, "No doctors found.")
        return redirect('doctors')

    context = {
        'doctors': doctors,
    }

    return render(request, 'doctors.html', context)


@login_required
def create_appointment(request, doctor_id):
    doctor = Doctor.objects.get(id=doctor_id)

    if request.method == 'POST':
        appointment_date = request.POST['appointment_date']
        description = request.POST['description']
        appointment_time_id = request.POST['appointment_time']
        time_slot = DoctorTimeSlot.objects.get(id=appointment_time_id, doctor=doctor)
        selected_date = timezone.datetime.strptime(appointment_date, '%Y-%m-%d').date()
        today = timezone.now().date()

        if not doctor.status:
            doctor.available_spots = doctor.available_spots + 1
            doctor.status = True
            doctor.save()
            # Doctor is unavailable
            if selected_date < doctor.next_available_appointment_date:
                messages.error(request,
                               f"Choose a date after: {doctor.next_available_appointment_date.strftime('%d/%B/%Y')}")
                return redirect(reverse('create_appointment', args=[doctor_id]))
        else:
            if selected_date < today:
                messages.error(request, "Please select an upcoming date.")
                return redirect(reverse('create_appointment', args=[doctor_id]))

        if doctor.available_spots == 0:
            doctor.status = False
        else:
            doctor.status = True
        doctor.save()

        serial_number = Appointment.objects.filter(doctor=doctor).count() + 1

        appointment = Appointment(
            user=request.user,
            doctor=doctor,
            appointment_date=appointment_date,
            description=description,
            doctor_time_slot=time_slot,
            serial_number=serial_number
        )
        appointment.save()

        doctor.available_spots -= 1
        if doctor.available_spots == 0:
            doctor.status = False
        else:
            doctor.status = True
        doctor.save()

        messages.success(request, "Successful appointment made")
        return redirect(reverse('doctors'))

    context = {
        'doctor': doctor
    }
    return render(request, 'create_appointment.html', context)


def cancel_appointment(request, appointment_id, doctor_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    doctor = get_object_or_404(Doctor, id=doctor_id)

    if appointment.user == request.user:
        doctor.available_spots += 1
        doctor.save()
        appointment.serial_number -= 1
        appointment.delete()
        messages.success(request, "Appointment canceled successfully.")
    else:
        messages.error(request, "You are not authorized to cancel this appointment.")

    return redirect('user_profile')



# Medicine function start
def products(request):
    products = Medicines.objects.all()

    context = {
        'products': products,
    }

    return render(request, 'medicines.html', context)

def product_search(request):
    query = request.GET.get('q')

    if query:
        products = Medicines.objects.filter(
            Q(p_name__icontains=query) | Q(p_description__icontains=query)
        )
    else:
        messages.error(request, "Search bar was empty")
        return redirect('medicines')

    if not products:
        messages.error(request, "No product found")
        return redirect('medicines')

    context = {
        'products': products,
    }

    return render(request, 'medicines.html', context)


