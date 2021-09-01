import json
from django.contrib.auth import logout

from django.core import serializers
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
import requests
from requests.auth import HTTPBasicAuth
import africastalking


# Create your views here.
from django.views.generic import TemplateView

from mat360.settings import AFRICAS_TALKING_USERNAME, AFRICAS_TALKING_API_KEY
from sacco_manager.models import Vehicle, Sacco, Route, StageController
from stagecontroller.models import FareUpdate
from sacco_manager.algorithms.algo import FilterClass
from sacco_manager.algorithms.Universal import ValidationCheck

#Create Instance
validI=ValidationCheck()


class Index(TemplateView):
    template_name = 'index.html'
class Saccos(TemplateView):
    template_name = 'saccos.html'
def book_ride(request):
    if request.method=='POST':
        request.session['vehicle_id']=request.POST['rideNumber']
        request.session['departure']=request.POST['departure']
        request.session['destination'] = request.POST['destination']
        return redirect('home:signin')
    return render(request,'book_ride.html',{'stations':validI.getallroutes()})
def process_login(request):
    return render(request,'signin.html')
def create_account(request):
    return render(request,'signup.html')

def check_saccos(request):
    departure =request.GET.get('departure', None)
    destination=request.GET.get('destination',None)

    #Final values to query
    d_departure=''
    d_destination=''

    filterI=FilterClass()

    if filterI.prepare_town_search(departure,destination):
        d_departure=departure.upper()
        d_destination=destination.upper()
    else:
        d_departure=destination.upper()
        d_destination=departure.upper()
    result_set=[]
    #all_saccos=Sacco.objects.all()
    all_saccos=Route.objects.filter(departure=d_departure).filter(destination=d_destination)
    for sacco in all_saccos:
        result_set.append({'name':sacco.sacco.sacco_name,'regnumber':sacco.sacco.sacco_reg_no})
    #data={'vehicle':serializers.serialize('json',)}
    return  HttpResponse(json.dumps(result_set),content_type='application/json')


def get_sacco_rides(request):
    sacoNo=request.GET.get('sacco',None)
    departure=request.GET.get('departure',None)
    destination = request.GET.get('destination', None)
    d_departure = ''
    d_destination = ''
    filterI = FilterClass()
    if filterI.prepare_town_search(departure, destination):
        d_departure = departure.upper()
        d_destination = destination.upper()
    else:
        d_departure = destination.upper()
        d_destination = departure.upper()
    sacco = Sacco.objects.get(sacco_reg_no=sacoNo)
    routeI=Route.objects.get(Q(departure=d_departure),Q(destination=d_destination),Q(sacco=sacco))
    result_set=[]
    #all_saccos=Sacco.objects.all()

    all_rides=Vehicle.objects.filter(sacco=sacco).filter(route=routeI).filter(vcontrol__station=departure.upper()).filter(vcontrol__controller_confirmation_status=True).filter(vehiclestatus__status=None)
    for ride in all_rides:
        result_set.append({'vnumber':ride.v_number})
    #data={'vehicle':serializers.serialize('json',)}
    return  HttpResponse(json.dumps(result_set),content_type='application/json')







#Get three properties of the selected ride,total_capacity,active_fare and active bookings.
def get_ride_important_details(request):
    #Values from front end.
    v_number=request.GET.get('vnumber',None)
    departure=request.GET.get('departure',None)
    destination = request.GET.get('destination', None)
    sacco_reg=request.GET.get('saccoreg', None)

    #Get the capacity.
    v_list=list(Vehicle.objects.filter(pk=v_number).values_list('capacity',flat=True))
    capacity=v_list[0]
    d_departure = ''
    d_destination = ''
    filterI = FilterClass()
    if filterI.prepare_town_search(departure, destination):
        d_departure = departure.upper()
        d_destination = destination.upper()
    else:
        d_departure = destination.upper()
        d_destination = departure.upper()
    #Get Route;
    sacco = Sacco.objects.get(pk=sacco_reg)
    routeI = Route.objects.get(Q(departure=d_departure), Q(destination=d_destination), Q(sacco=sacco))
    stagecontrolerI=StageController.objects.get(Q(station=departure.upper()),Q(sacco=sacco))
    fareI=FareUpdate.objects.filter(Q(route=routeI),Q(sacco=sacco),Q(stagecontroller=stagecontrolerI)).latest('created')
    fareAmount=str(fareI.amount)
    bookings=validI.get_bookings_per_ride(v_number)

    #Function to hold active bookings willcome here;
    v_details=[]
    v_details.append({'capacity':capacity,'fareamount':fareAmount,'tbookings':bookings})

    return HttpResponse(json.dumps(v_details), content_type='application/json')




def getActivePrice(request):
    #vehicle_no=request.GET.get('vnumber',None)
    sacco=request.GET.get('sacco',None)
    departureT=request.GET.get('departure',None)
    destinationT=request.GET.get('destination',None)
    routeI=Route.objects.get(Q(departure=departureT.upper()),Q(destination=destinationT.upper()))
    saccoI=Sacco.objects.get(sacco_name=sacco)
    result_set=[]

    try:
        fareUpdateI=FareUpdate.objects.filter(Q(route=routeI.id),Q(sacco=saccoI.id)).latest('created')
        result_set.append({'active_fare':fareUpdateI.amount})
    except FareUpdate.DoesNotExist:
        result_set.append({'active_fare': None})
    return HttpResponse(json.dumps(result_set), content_type='application/json')






def mpesaSimulate(request):
    #generaing access tokens;
    consumer_key = "hGIRSPOmGh4gQpggg9gUdQUP7TEob1yz"
    consumer_secret = "4iPmR7fPaxGYEwJ1"
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    myr=json.loads(r.text)
    access_token=myr["access_token"]
    api_url = "http://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers = {"Authorization": "Bearer %s" % access_token}
    request = {"ShortCode": "60502",
               "ResponseType": "Completed",
               "ConfirmationURL": "http://aa2e571b3b98.ngrok.io/confirmation/",
               "ValidationURL": "http://aa2e571b3b98.ngrok.io/validation/"}
    response = requests.post(api_url, json=request, headers=headers)
    return HttpResponse(response.text)

    #print(r.text)
def confirmation_url(request):
    myresponse={
          "ResultCode": 0,
          "ResultDesc": "Accepted"
        }
    return HttpResponse(json.dumps(myresponse), content_type='application/json')

def validation_url(request):
    confirmation_response={
        "C2BPaymentConfirmationResult": "Success"
    }
    return HttpResponse(json.dumps(confirmation_response), content_type='application/json')




#AFRICASTALKING PAYMENT

def process_payment(request):
    username="sandbox "
    api_key="31c118383e9d42b1cc179cd5d7fe413ace1e3e1b223264764fcd8ed705ff3213"
    africastalking.initialize(username, api_key)
    pay=africastalking.Payment

    product_name = "Travel"
    phone_number = "+254794249057"
    currency_code = "KES"
    amount = 250
    response={}

    try:
        response = pay.mobile_checkout(product_name, phone_number, currency_code, amount)
        print(response)
    except Exception as e:
        response=e
    return HttpResponse(response)




def logout_view(request):
    logout(request)
    return redirect('home:signin')




