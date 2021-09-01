import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView

from mat360admin.models import Mat360SystemUsers,Payments
from mat360admin.core.payments import MpesaClient
from sacco_manager.algorithms.finances import FinancesSavingOperations
from sacco_manager.algorithms.travellerOR import TravellerOperations
from sacco_manager.models import Vehicle, VehicleBookings, VehicleStatus
from sacco_manager.algorithms.Universal import ValidationCheck
from django.views.decorators.csrf import csrf_exempt

''''
This will involve all views that are related to customers .
1.Registration of customers to the database.
2.Processing customer Login
3.Making bookings and paying fees using MPESA.
4.Display of customer receipts  and history of travel.
'''
validI=ValidationCheck()
mpesa_client=MpesaClient()
toperations=TravellerOperations()

def create_customer_account(request):
    if  request.method == 'POST':
        fname=request.POST['fname']
        lname = request.POST['lname']
        phone = request.POST['phone']
        password = request.POST['password']
        cpassword=request.POST['cpassword']

        if password !=cpassword:
            messages.error(request,'ERROR. Passwords do not match.')
        else:
            Mat360SystemUsers.objects.create(
                first_name=fname,
                last_name=lname,
                username=phone,
                password=make_password(password,salt=None),
                is_customer=True
            )
            messages.success(request,'Your account has been succesfully created. You can now login by clicking the link below.')






    return render(request,'signup.html',locals())


#Login the driver of the
def log_user_in(request):
    if request.method == 'POST':
        user=authenticate(username=request.POST['username'],password=request.POST['pass'])
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('mat360admin:admin-dash')
            elif user.is_staff and user.is_saccomanager:
                return redirect('sacco_manager:sacco-manager-dashboard')
            elif user.is_stagecontroller:
                return redirect('stagecontroller:stagecontroller-dashboard')
            elif user.is_driver:
                return redirect('driver:index')

            elif user.is_customer:
                return redirect('traveller:t-dash')
                #process traveller.


        else:
            messages.error(request,'ERROR. You have entered wrong login credentials.')


    return render(request,'signin.html')

@login_required(login_url='home:signin')
def load_traveller_dashboard(request):
    total_expenses=toperations.getTotalTransportExpense(request.user)

    return  render(request,'traveller/home.html',{'t_expense':total_expenses})
@login_required(login_url='home:signin')
def home_book_ride(request):
    if request.method=='POST':
        request.session['vehicle_id']=request.POST['rideNumber']
        request.session['departure']=request.POST['departure']
        request.session['destination'] = request.POST['destination']
        request.session['saccoName'] = request.POST['saccoName']
        request.session['amount'] = request.POST['amount']
        return redirect('traveller:pay_ride')
    return render(request,'traveller/book_ride.html',{'stations':validI.getallroutes()})
@login_required(login_url='home:signin')
@csrf_exempt
def pay_your_ride(request):
    response=""
    if request.method == 'POST':
        vnumber=request.session.get('vehicle_id')
        confirmation_code=request.POST['c_code']
        vehicleI=Vehicle.objects.get(pk=vnumber)
        user=Mat360SystemUsers.objects.get(username=request.user.username)
        if validI.prevent_double_booking(user,vehicleI,confirmation_code):
            messages.error(request,"OOPS! .You cannot make another booking because you already have an active booking.")
        else:
            #Confirm is the payment is successful
            if(Payments.objects.filter(booking_code=confirmation_code).filter(bill_refnumber=vehicleI).filter(user=request.user).exists()):
                #Update the payment status to be true
                VehicleBookings.objects.filter(booking_code=confirmation_code).filter(vehicle=vehicleI).filter(traveller=request.user).update(payment_status=True)
                messages.success(request,"Your booking was successful.Kindly maintain a considerable distance from stage.You will get an sms when your ride is ready to leave stage.")            
            else:                
                messages.error(request,"Wrong Business confirmation code")


        #Check if the number of bookings is equivalent to the maximum capacity.
        if validI.get_bookings_per_ride(vnumber) == int(vehicleI.capacity):
            VehicleStatus.objects.create(vehicle=vehicleI,status='full')
            #We send sms to every member;
            all_users=VehicleBookings.objects.filter(vehicle=vehicleI)
            for user in all_users:
                response=validI.sendSms(user.traveller.username,user.traveller.first_name,user.traveller.last_name)


        #Save the details to database now.
    return render(request,'traveller/pay_ride.html',{'v_number':request.session.get('vehicle_id'),'sacco_name':request.session.get('saccoName'),'amount':request.session.get('amount'),'departure':request.session.get('departure'),'destination':request.session.get('destination'),'response':response})

@login_required(login_url='home:signin')
def my_rides(request):
    tvOps=TravellerOperations()
    user = Mat360SystemUsers.objects.get(username=request.user.username)
    all_rides=tvOps.get_my_rides(user)
    return  render(request,'traveller/my_rides.html',{'all_rides':all_rides})















