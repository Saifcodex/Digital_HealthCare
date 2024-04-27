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


@login_required
def cart(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    for item in cart_items:
        item.total_cost = item.accessory.p_cost * item.quantity

    total_cost = sum(item.total_cost for item in cart_items)

    context = {
        'cart_items': cart_items,
        'total_cost': total_cost
    }
    return render(request, 'cart.html', context)


@login_required
def add_to_cart(request, product_id):
    if request.method == 'POST':
        user = request.user
        product = get_object_or_404(Medicines, pk=product_id)
        quantity = int(request.POST.get('quantity', 0))

        if quantity <= 0:
            messages.error(request, "Add at least 1 item!")
            return redirect(reverse('products'))

        if quantity > product.p_count:
            messages.error(request, "Out of stock!")
            return redirect(reverse('products'))

        cart_item, created = CartItem.objects.get_or_create(user=user, accessory=product)

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.total_cost = cart_item.quantity * cart_item.accessory.p_cost
        cart_item.save()
        messages.success(request, "Successfully added")
        return redirect(reverse('products'))
    else:
        return redirect('products')

    @login_required
    def remove_from_cart(request, product_id):
        if request.method == 'POST':
            user = request.user
            product = get_object_or_404(Medicines, pk=product_id)
            cart_item = CartItem.objects.get(user=user, accessory=product)
            cart_item.delete()
            messages.success(request, "Item removed from your cart.")
        return redirect('cart')

    @login_required
    def update_cart(request, product_id):
        if request.method == 'POST':
            user = request.user
            product = get_object_or_404(Medicines, pk=product_id)
            quantity = int(request.POST.get('quantity', 1))
            cart_item = CartItem.objects.get(user=user, accessory=product)

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.total_cost = cart_item.quantity * cart_item.accessory.p_cost
                cart_item.save()
                messages.success(request, "Cart item updated.")
            else:
                cart_item.delete()
                messages.success(request, "Item removed from your cart.")
            cart_item = CartItem.objects.get(user=user, accessory=product)

        return redirect('cart')

    @login_required
    def checkout(request):
        user = request.user
        cart_items = CartItem.objects.filter(user=user)

        new_bill = Bill.objects.create(customer=user, total_cost=0, created_at=timezone.now())

        for item in cart_items:
            if item.accessory.p_count >= item.quantity:
                item.accessory.p_count -= item.quantity
                item.accessory.save()
                BillItem.objects.create(
                    bill=new_bill,
                    accessory=item.accessory,
                    quantity=item.quantity,
                    total_cost=item.total_cost
                )

        new_bill.save()
        cart_items.delete()
        messages.success(request, "Checkout successful.")
        context = {
            'new_bill': new_bill,
        }
        return render(request, 'checkout.html', context)


