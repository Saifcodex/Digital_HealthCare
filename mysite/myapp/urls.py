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

# product urls
    path('products/', views.products, name='products'),
    path('product_search/', views.product_search, name='product_search'),
    path('cart/', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('update_cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),


# doctor appointment urls
    path('doctors/', views.doctors, name='doctors'),
    path('doctor_search/', views.doctor_search, name='doctor_search'),
    path('create_appointment/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('cancel_appointment/<int:appointment_id>/<int:doctor_id>/', views.cancel_appointment, name='cancel_appointment'),


]