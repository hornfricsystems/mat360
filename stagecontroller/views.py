from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.timezone import now
from django.views.generic import TemplateView
from sacco_manager.models import Vehicle, VControl, Route, Sacco, StageController
from sacco_manager.algorithms.algo import FilterClass
from stagecontroller.models import FareUpdate



#This is the function to confirm available rides
@login_required(login_url='admin:admin-login')
def avail_driver_activated_rides(request):
    try:
        all_rides=VControl.objects.filter(v_availability_by_driver=True).filter(controller_confirmation_status=False).filter(station=request.user.stagecontroller.station)
    except VControl.DoesNotExist:
        all_rides=None

    if request.method == 'POST':
        VControl.objects.filter(pk=request.POST['v_id']).update(controller_confirmation_status=True,time_of_confirmation_by_controller=now())
        messages.success(request,'Vehicle activated successfully')
    return render(request,'stage_controller/activate_driver_requests.html',{'rides':all_rides})
@login_required(login_url='admin:admin-login')
def update_fare(request):
    dapartureT= request.user.stagecontroller.station

    #Get all the updated rides
    stagecontrollerI = StageController.objects.get(pk=request.user.stagecontroller.id_number)
    activeFareI=FareUpdate.objects.filter(stagecontroller=stagecontrollerI)


    #destinations=Route.objects.filter(Q(departure= dapartureT.upper())| Q(destination= dapartureT.upper()) ).values_list('departure',flat=True).distinct()
    if request.method == 'POST':
        departuretown=request.POST['from']
        destinationT=request.POST['destination']
        amount=request.POST['amount']

        d_departure = ''
        d_destination = ''
        filterI = FilterClass()
        if filterI.prepare_town_search(departuretown, destinationT):
            d_departure = departuretown.upper()
            d_destination = destinationT.upper()
        else:
            d_departure = destinationT.upper()
            d_destination = departuretown.upper()
        try:
            sacco=Sacco.objects.get(pk=request.user.stagecontroller.sacco.sacco_reg_no)
            route=Route.objects.get(Q(departure=d_departure),Q(destination=d_destination),Q(sacco=request.user.stagecontroller.sacco.sacco_reg_no))

            fareupdate = FareUpdate()
            fareupdate.sacco = sacco
            fareupdate.route = route
            fareupdate.stagecontroller=stagecontrollerI
            fareupdate.amount = amount
            fareupdate.save()
            messages.success(request, 'Your Fare has been updated successfuly')
        except Route.DoesNotExist:
            messages.error(request,"The route is not registered by the sacco")


    return render(request,'stage_controller/update_fare.html',{'fare':activeFareI})
@login_required(login_url='admin:admin-login')
def get_active_rides(request):
    stagecontrollerI = StageController.objects.get(pk=request.user.stagecontroller.id_number)
    sacco = Sacco.objects.get(pk=request.user.stagecontroller.sacco.sacco_reg_no)
    active_rides=Vehicle.objects.filter(vcontrol__station=stagecontrollerI.station).filter(vcontrol__controller_confirmation_status=True).filter(sacco=sacco)
   # total_rides=Vehicle.objects.filter(vcontrol__station=stagecontrollerI.station).filter(vcontrol__controller_confirmation_status=True).filter(sacco=sacco).count()

    return render(request, 'stage_controller/activated_rides.html', {'activerides': active_rides,'totalrides':range(active_rides.count())})
