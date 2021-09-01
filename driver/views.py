from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from django.utils.timezone import now

from sacco_manager.models import Vehicle, VControl, Route


@login_required(login_url='login')
def index(request):
    #get the vehicle status
    status=False
    vobject=Vehicle.objects.get(v_number=request.user.driver.driver.v_number)
    route_depart=vobject.route.departure
    route_dest = vobject.route.destination

    available_towns=[route_depart,route_dest]




    try:
        vcontrol=VControl.objects.filter(vehicle=request.user.driver.driver.v_number).latest('v_availability_by_driver');
        status=vcontrol.v_availability_by_driver
    except  VControl.DoesNotExist:
        status =False
    if request.method == 'POST':
        status=request.POST.get('status',None)
        station=request.POST.get('station',None)

        if status is None:
            messages.error(request,'You have not activated the ride')
        else:
            if prevent_redundant_activation_in_a_day(request,request.user.driver.driver.v_number)<=8:
                messages.error(request,'ERROR! Your ride should be on the road for atleast 8 hours:'+str(prevent_redundant_activation_in_a_day(request,request.user.driver.driver.v_number)))
            else:
                vehicle = Vehicle.objects.get(v_number=request.user.driver.driver.v_number)
                vcontrol=VControl()
                vcontrol.vehicle=vehicle
                vcontrol.station=station
                vcontrol.v_availability_by_driver=True
                vcontrol.controller_confirmation_status=False
                vcontrol.save()
                messages.success(request,'The vehicle has been activated'+str(vcontrol.time_available_by_driver))
    return render(request,'driver/dashboard.html',{'vstatus':status,'towns':available_towns})
#Function to prevent double entry and activation of active vehicle.
def prevent_redundant_activation_in_a_day(request,v_number):
    time_difference=0
    try:
        vehicle = VControl.objects.filter(vehicle=v_number).latest('time_available_by_driver')
        date_activated=vehicle.time_available_by_driver
        time_difference=(now()-date_activated).seconds/60/60
    except VControl.DoesNotExist:
        vehicle=None
        time_difference=10
    return  time_difference

