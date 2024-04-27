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

