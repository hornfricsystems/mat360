from django.urls import path

from stagecontroller import views
app_name='stagecontroller'

urlpatterns=[
    path('accounts/update_fare/',views.update_fare,name='update-fare'),
    path('accounts/available_rides/',views.avail_driver_activated_rides,name='confirm-driver-rides'),
    path('accounts/active_rides/',views.get_active_rides,name='activerides'),
]