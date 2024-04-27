from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView

from . import views


urlpatterns =[
    # admin and basic urls
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('FAQ/', views.FAQ, name='FAQ'),

    # user acc urls
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('logout/', views.logout, name='logout'),

# product urls
    path('products/', views.products, name='products'),
    path('product_search/', views.product_search, name='product_search'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    # Equipments
    path('equipments/', views.equipments, name='equipments'),
    path('equipment_search/', views.equipment_search, name='equipment_search'),
    path('cart1/', views.cart1, name='cart1'),
    path('add_to_cart1/<int:equipment_id>/', views.add_to_cart1, name='add_to_cart1'),
    path('update_cart1/<int:equipment_id>/', views.update_cart1, name='update_cart1'),
    path('remove_from_cart1/<int:equipment_id>/', views.remove_from_cart1, name='remove_from_cart1'),
    path('checkout1/', views.checkout1, name='checkout1'),


# doctor appointment urls
    path('doctors/', views.doctors, name='doctors'),
    path('doctor_search/', views.doctor_search, name='doctor_search'),
    path('create_appointment/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('cancel_appointment/<int:appointment_id>/<int:doctor_id>/', views.cancel_appointment, name='cancel_appointment'),

    # error handaling urls
    path('custom_error/', views.custom_error, name='custom_error'),
    path('<path:undefined_path>/', RedirectView.as_view(url='/custom_error/')),


]