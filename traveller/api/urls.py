from django.urls import path
from traveller.api.views import travellerRegistrationView
app_name='traveller'

urlpatterns=[
    path('register',travellerRegistrationView,name='pi_register'),
]