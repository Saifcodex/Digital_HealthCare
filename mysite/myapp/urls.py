


urlpatterns =[



# doctor appointment urls
    path('doctors/', views.doctors, name='doctors'),
    path('doctor_search/', views.doctor_search, name='doctor_search'),
    path('create_appointment/<int:doctor_id>/', views.create_appointment, name='create_appointment'),
    path('cancel_appointment/<int:appointment_id>/<int:doctor_id>/', views.cancel_appointment, name='cancel_appointment'),


]