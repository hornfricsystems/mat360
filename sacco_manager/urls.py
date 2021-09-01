from django.urls import path
from sacco_manager import views

app_name='sacco_manager'

urlpatterns=[
    path('request_sacco_registration/',views.save_sacco_registration_requests,name='request-sacco-registration'),
    path('accounts/',views.sacco_manager_dashboard,name='sacco-manager-dashboard'),
    path('accounts/new_vehicle',views.new_vehicle_registration,name='new-vehicle-registration'),
    path('accounts/our_fleet',views.get_fleet,name='our-fleet'),
    path('accounts/new_stage_controller', views.register_stage_controller, name='new-controller'),
    path('accounts/our_settings', views.sacco_settings, name="sacco-settings"),
    path('accounts/vehicle_statistics',views.vehicle_statistics,name='vehicle_stats'),
    #path('accounts/route-management/',views.route_management_home,name='route_management'),
    path('accounts/route-management/register_route', views.register_vehicle_route, name='register_route'),

    path('',views.logout_view,name='logout'),
]