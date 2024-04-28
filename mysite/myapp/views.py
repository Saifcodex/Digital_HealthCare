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

def custom_error(request, ):
    return render(request, 'error.html')


def login(request):
    if request.method == "POST":
        form = Captcha(request.POST)
        if form.is_valid():
            username = request.POST.get("u_name")
            password = request.POST.get("u_password")
            authenticated_user = authenticate(request, username=username, password=password)

            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                messages.success(request, f"Welcome, {username}!")
                return redirect("home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "reCAPTCHA verification failed. Please try again.")

    else:
        form = Captcha()

    return render(request, "login.html", {"form": form})


def register(request):
    if request.method == "POST":
        form = Captcha(request.POST)
        if form.is_valid():
            u_name = request.POST.get("u_name")
            u_fname = request.POST.get("u_fname")
            u_lname = request.POST.get("u_lname")
            u_email = request.POST.get("u_email")
            u_password = request.POST.get("u_password")
            u_age = request.POST.get("u_age")
            u_address = request.POST.get("u_address")
            u_mobile = request.POST.get("u_mobile")
            u_gender = request.POST.get("u_gender")

            user = User.objects.create_user(username=u_name, first_name=u_fname, last_name=u_lname, email=u_email,
                                            password=u_password)
            user.save()
            user_profile = UserProfile(user=user, age=u_age, address=u_address, mobile=u_mobile, gender=u_gender)
            user_profile.save()

            authenticated_user = authenticate(request, username=u_name, password=u_password)

            if authenticated_user is not None:
                auth_login(request, authenticated_user)
                messages.success(request, "Your account has been successfully created.")
                return redirect("home")
            else:
                messages.error(request, "User registration failed. Please try again.")
        else:
            messages.error(request, "reCAPTCHA verification failed. Please try again.")

    else:
        form = Captcha()

    return render(request, "register.html", {"form": form})


from django.db.models import Sum


def user_profile(request):
    user_profile = UserProfile.objects.get(user=request.user)
    profile_form = UserProfileForm(instance=user_profile)
    user_form = UserForm(instance=request.user)
    appointments = Appointment.objects.filter(user=request.user)
    bookings = Booking.objects.filter(user=request.user)

    # Use a different name for the annotated field, e.g., 'total_item_cost'
    bills = Bill.objects.filter(customer=request.user).prefetch_related(
        Prefetch('billitem_set', queryset=BillItem.objects.select_related('accessory'))
    ).annotate(total_item_cost=Sum('billitem__total_cost'))

    bills1 = Bill1.objects.filter(customer=request.user).prefetch_related(
        Prefetch('billitem1_set', queryset=BillItem1.objects.select_related('accessory1'))
    ).annotate(total_item_cost1=Sum('billitem1__total_cost1'))

    if request.method == "POST":
        if "delete_account" in request.POST:
            request.user.delete()
            auth_logout(request)
            messages.success(request, "Your account has been deleted.")
            return redirect('login')

        profile_form = UserProfileForm(request.POST, instance=user_profile)
        user_form = UserForm(request.POST, instance=request.user)

        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('user_profile')
        else:
            messages.error(request, "Error updating profile. Please check the form.")

    context = {
        'user_profile': user_profile,
        'profile_form': profile_form,
        'user_form': user_form,
        'appointments': appointments,
        'bills': bills,
        'bills1': bills1,
        'bookings': bookings,
    }
    return render(request, 'user_profile.html', context)


@login_required
def logout(request):
    user = request.user
    CartItem.objects.filter(user=user).delete()
    auth_logout(request)
    messages.success(request, "Logged out Successfully!")
    return redirect('home')


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


def donors(request):
    donor = Donor.objects.all()
    return render(request, 'blood_donors.html', {'donor': donor})

def blood_search(request):
    query = request.GET.get('q')
    donor = Donor.objects.all()

    if query:
        donor = Donor.objects.filter(
            Q(bloodgroup__iexact=query)
        ).distinct()
    else:
        messages.error(request, "Search bar was empty")
        return redirect('blood_donors')

    if not donor:
        messages.error(request, "No blood donors found.")
        return redirect('blood_donors')

    context = {
        'donor': donor,
    }
    return render(request, 'blood_donors.html', context)



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


# Equipments

def equipments(request):
    equipments = Equipments.objects.all()

    context = {
        'equipments': equipments,
    }

    return render(request, 'equipments.html', context)

def equipment_search(request):
    query1 = request.GET.get('q')

    if query1:
        equipments = Equipments.objects.filter(
            Q(e_name__icontains=query1) | Q(e_description__icontains=query1)
        )
    else:
        messages.error(request, "Search bar was empty")
        return redirect('equipments')

    if not equipments:
        messages.error(request, "No product found")
        return redirect('equipments')

    context = {
        'equipments': equipments,
    }

    return render(request, 'equipments.html', context)

@login_required
def cart1(request):
    user = request.user
    cart_items1 = CartItem1.objects.filter(user=user)

    for item1 in cart_items1:
        item1.total_cost1 = item1.accessory1.e_cost * item1.quantity1

    total_cost1 = sum(item1.total_cost1 for item1 in cart_items1)

    context = {
        'cart_items1': cart_items1,
        'total_cost1': total_cost1
    }
    return render(request, 'cart1.html', context)

@login_required
def add_to_cart1(request, equipment_id):
    if request.method == 'POST':
        user = request.user
        equipments = get_object_or_404(Equipments, pk=equipment_id)
        quantity1 = int(request.POST.get('quantity1', 0))

        if quantity1 <= 0:
            messages.error(request, "Add at least 1 item!")
            return redirect(reverse('equipments'))

        if quantity1 > equipments.e_count:
            messages.error(request, "Out of stock!")
            return redirect(reverse('equipments'))

        cart_item1, created = CartItem1.objects.get_or_create(user=user, accessory1=equipments)

        if created:
            cart_item1.quantity1 = quantity1
        else:
            cart_item1.quantity1 += quantity1

        cart_item1.total_cost1 = cart_item1.quantity1 * cart_item1.accessory1.e_cost
        cart_item1.save()
        messages.success(request, "Successfully added")
        return redirect(reverse('equipments'))
    else:
        return redirect('equipments')

@login_required
def remove_from_cart1(request, equipment_id):
    if request.method == 'POST':
        user = request.user
        equipments = get_object_or_404(Equipments, pk=equipment_id)
        cart_item1 = CartItem1.objects.get(user=user, accessory1=equipments)
        cart_item1.delete()
        messages.success(request, "Item removed from your cart.")
    return redirect('cart1')

@login_required
def update_cart1(request, equipment_id):
    if request.method == 'POST':
        user = request.user
        equipments = get_object_or_404(Equipments, pk=equipment_id)
        quantity1 = int(request.POST.get('quantity1', 1))
        cart_item1 = CartItem1.objects.get(user=user, accessory1=equipments)

        if quantity1 > 0:
            cart_item1.quantity1 = quantity1
            cart_item1.total_cost1 = cart_item1.quantity1 * cart_item1.accessory1.e_cost
            cart_item1.save()
            messages.success(request, "Cart item updated.")
        else:
            cart_item1.delete()
            messages.success(request, "Item removed from your cart.")
        cart_item1 = CartItem1.objects.get(user=user, accessory1=equipments)

    return redirect('cart1')

@login_required
def checkout1(request):
    user = request.user
    cart_items1 = CartItem1.objects.filter(user=user)

    new_bill1 = Bill1.objects.create(customer=user, total_cost1=0, created_at=timezone.now())

    for item1 in cart_items1:
        if item1.accessory1.e_count >= item1.quantity1:
            item1.accessory1.e_count -= item1.quantity1
            item1.accessory1.save()
            BillItem1.objects.create(
                bill1=new_bill1,
                accessory1=item1.accessory1,
                quantity1=item1.quantity1,
                total_cost1=item1.total_cost1
            )

    new_bill1.save()
    cart_items1.delete()
    messages.success(request, "Checkout successful.")
    context = {
        'new_bill1': new_bill1,
    }
    return render(request, 'checkout1.html', context)

def beds(request):
    beds = Bed.objects.all()
    context = {
        'beds': beds
    }
    return render(request, "beds.html", context)

def bed_search(request):
    query_b = request.GET.get('q')

    if query_b:
        words = query_b.split()
        bed_query = Q()
        status_query = Q()

        for word in words:
            if word.lower() == "available":
                status_query = Q(status=True)

            elif word.lower() == "unavailable":
                status_query = Q(status=False)

            else:
                bed_query |= Q(bed_type__icontains=word)

        beds = Bed.objects.filter(bed_query, status_query)
    else:
        messages.error(request, "Search bar was empty")
        return redirect('beds')

    if not doctors:
        messages.error(request, "No beds found.")
        return redirect('beds')

    context = {
        'beds': beds,
    }

    return render(request, 'beds.html', context)

@login_required
def create_booking(request, bed_id):
    bed = Bed.objects.get(id=bed_id)

    if request.method == 'POST':
        booking_date = request.POST['booking_date']
        description1 = request.POST['description1']
        # booking_time_id = request.POST['booking_time']
        # time_slot1 = BedTimeSlot.objects.get(id=booking_time_id, bed=bed)
        selected_date1 = timezone.datetime.strptime(booking_date, '%Y-%m-%d').date()
        today1 = timezone.now().date()

        if not bed.status1:
            bed.available_spots1 = bed.available_spots1 + 1
            bed.status1 = True
            bed.save()

            if selected_date1 < bed.available_booking_date:
                messages.error(request,
                               f"Choose a date after: {bed.available_booking_date.strftime('%d/%B/%Y')}")
                return redirect(reverse('create_booking', args=[bed_id]))
        else:
            if selected_date1 < today1:
                messages.error(request, "Please select an upcoming date.")
                return redirect(reverse('create_booking', args=[bed_id]))

        if bed.available_spots1 == 0:
            bed.status1 = False
        else:
            bed.status1 = True
        bed.save()

        serial_number1 = Booking.objects.filter(bed=bed).count() + 1

        booking = Booking(
            user=request.user,
            bed=bed,
            booking_date=booking_date,
            description1=description1,
            # bed_time_slot=time_slot1,
            serial_number1=serial_number1,
        )
        booking.save()

        bed.available_spots1 -= 1
        if bed.available_spots1 == 0:
            bed.status1 = False
        else:
            bed.status1 = True
        bed.save()

        messages.success(request, "Successfully booked")
        return redirect(reverse('beds'))

    context = {
        'bed': bed
    }
    return render(request, 'create_booking.html', context)

def cancel_booking(request, booking_id, bed_id):
    booking = get_object_or_404(Booking, id=booking_id)
    bed = get_object_or_404(Bed, id=bed_id)

    if booking.user == request.user:
        bed.available_spots1 += 1
        bed.save()
        booking.serial_number1 -= 1
        booking.delete()
        messages.success(request, "Booking canceled successfully.")
    else:
        messages.error(request, "You are not authorized to cancel this booking.")

    return redirect('user_profile')