import datetime
import json

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from mat360.settings import EMAIL_HOST_USER
from mat360admin.core.decorators import user_is_administrator
from mat360admin.models import Mat360SystemUsers, Payments
from sacco_manager.models import SaccoRegistrationRequests, SaccoManager, Sacco,Vehicle,VehicleBookings,VehicleStatus
from mat360admin.core.payments import MpesaClient,Mat360FinancialAnalysis
from sacco_manager.algorithms.Universal import ValidationCheck
from datetime import datetime
import random
#Create object of the Mpesa Client
client=MpesaClient()
validation_check=ValidationCheck()
financialAnalysis=Mat360FinancialAnalysis()

class AdminLogin(TemplateView):
    template_name = 'admin-in.html'


# This is the View to Login Admin
def log_admin_in(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['pass'])
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('mat360admin:admin-dash')
            elif user.is_staff and user.is_saccomanager:
                return redirect('sacco_manager:sacco-manager-dashboard')
            elif user.is_stagecontroller:
                return redirect('stagecontroller:confirm-driver-rides')
            elif user.is_driver:
                return redirect('driver:index')

            elif user.is_customer:
                pass
                # process traveller.


        else:
            messages.error(request, "Wrong username or password combination")
    return render(request, 'admin-login.html')


@login_required(login_url='/admin')
def load_admin_dash(request):
    return render(request, 'admin/new_sacco_manager.html')


@login_required(login_url='/admin')
@user_is_administrator
def view_sacco_requests_applications_and_approve(request):
    sacco_requests = SaccoRegistrationRequests.objects.all().filter(application_status='in_progress')
    if request.method == 'POST':
        user = Mat360SystemUsers()
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.username = request.POST['phone']
        user.email = request.POST['email']
        user.is_staff = True
        user.is_saccomanager = True
        user.user_type = 4
        user.password = make_password(request.POST['id_number'])
        user.save()

        # Save the other details to the user profile table.
        sacco_manager = SaccoManager()
        my_user = Mat360SystemUsers.objects.get(username=request.POST['phone'])
        sacco_manager.user = my_user
        sacco_manager.id_number = request.POST['id_number']
        sacco_manager.save()

        # Save Sacco Details
        sacco = Sacco()
        sacco_manager = SaccoManager.objects.get(pk=request.POST['id_number'])
        sacco.sacco_manager = sacco_manager
        sacco.sacco_reg_no = request.POST['reg_no']
        sacco.sacco_name = request.POST['sacco_name']
        sacco.save()

        # Update the table to have status as approved.
        SaccoRegistrationRequests.objects.filter(email_address=request.POST['email']).update(
            application_status='approved')
        # Email Details
        context = {
             'full_name': request.POST['first_name'] + '  ' + request.POST['last_name'],
             'username': request.POST['phone'],
             'password': request.POST['id_number'],

        }
        subject = "SACCO SERVICE REQUEST APPROVED."
        html_content = render_to_string('sacco_manager/saccomanager_mail.html', context)
        text_content = strip_tags(html_content)
        from_email = EMAIL_HOST_USER
        msg_html = render_to_string('sacco_manager/saccomanager_mail.html', context)
        to = [request.POST['email']]
        send_mail(subject, None, from_email, to, html_message=msg_html, fail_silently=True)

    return render(request, 'admin/sacco_application_requests.html', {'sacco_requests': sacco_requests})


''''
This is a view to approve an application.The approval process is just splitting the details that
the sacco manager submitted to us and feed them on three different tables.
1.The authentication table is fed with the following.
   Email_address,first_name,last_name,phone_number(will be used as a username).
2.User_Profile Table.
Will be related to the authentication table and will have .
 .ID_Number,user_type,approval date.
3.Sacco Details.
Will be related to the User_Profile table.
  .Sacco registration no.
  .Sacco Name.


'''


def create_system_admin(request):
    user = Mat360SystemUsers()
    user.username = 'mat360admin'
    user.email = 'mat360@admin.com'
    user.password = make_password('Korir9993')
    user.is_superuser = True
    user.user_type = 0
    user.save()
    print('Successfully create')
    return render(request, 'home.html')

@method_decorator(user_is_administrator,name='dispatch')
class ApprovedSaccoRequests(ListView):
    model =SaccoRegistrationRequests
    template_name = 'admin/approved_sacco_managers.html'

    def get_context_data(self, **kwargs):
        context=super(ApprovedSaccoRequests, self).get_context_data(**kwargs)
        context['approved']=SaccoRegistrationRequests.objects.filter(application_status='approved')
        return context
'''
These are admin and mpesa related views
'''
@csrf_exempt
def register_urls(request):
    api_URL="https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    headers= headers = {"Authorization": "Bearer %s" % client.generateMpesaAccessToken()}
    options={
        "ShortCode":"600980",
        "ResponseType":"Completed",        
        "ConfirmationURL":"https://65e4-102-166-44-63.ngrok.io/admin/c2b/confirmation",
        "ValidationURL":"https://65e4-102-166-44-63.ngrok.io/admin/c2b/validation",
    }
    response=requests.post(api_URL,json=options,headers=headers)
    return HttpResponse(response.text)

@csrf_exempt
def validation(request):
    context={
        "ResultCode":0,
        "ResultDesc":"Accepted"
    }
    return JsonResponse(dict(context))
    
#This is function to  handle the response from Mpesa.
@csrf_exempt
def confirmation(request):
    print("The confirmation has been hit")
    mpesa_body=request.body
    mpesa_payment_response=json.loads(mpesa_body)
    confirmation_code=random.randint(1000,9999)
    #Get all to variables
    transType=mpesa_payment_response['TransactionType']
    transID = mpesa_payment_response['TransID']
    transaction_time_string = mpesa_payment_response['TransTime']
    amount = mpesa_payment_response['TransAmount']
    business_code = mpesa_payment_response['BusinessShortCode']
    vehicle_number = mpesa_payment_response['BillRefNumber']
    invoice_number = mpesa_payment_response['InvoiceNumber']
    msisdn = mpesa_payment_response['MSISDN']
    fname = mpesa_payment_response['FirstName']
    mname = mpesa_payment_response['MiddleName']
    lname = mpesa_payment_response['LastName']
    #Data manipulation
    user=Mat360SystemUsers.objects.get(username=msisdn)
    vehicle=Vehicle.objects.get(v_number=vehicle_number)
    transaction_date=datetime.strptime(transaction_time_string,"%Y%m%d%H%M%S")

    payments=Payments()
    payments.user=user
    payments.transaction_type=transType
    payments.transaction_id=transID
    payments.transaction_time=transaction_date
    payments.transaction_amount=amount
    payments.business_shortcode = business_code
    payments.bill_refnumber = vehicle
    payments.invoice_number = invoice_number
    payments.msisdn = msisdn
    payments.first_name = fname
    payments.middle_name = mname
    payments.last_name = lname
    payments.booking_code=confirmation_code
    payments.save() 
    #Send an sms to the number that has paid with the confirmation code.
    validation_check.sendMpesaConfirmationCode("0794249057",confirmation_code)
    #Booking should be automatically used to book the vehicle.
    VehicleBookings.objects.create(vehicle=vehicle,traveller=user,booking_code=confirmation_code)


    return JsonResponse("Successfully Saved")
@csrf_exempt
def simulatec2b(request):
    api_URL="https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
    headers = {"Authorization": "Bearer %s" % client.generateMpesaAccessToken()}
    options={
        "CommandID":"CustomerPayBillOnline",
        "Amount":400,
        "Msisdn":254708374149,
        "BillRefNumber":"KCA001A",
        "ShortCode":"600987",
    }
    response=requests.post(api_URL,json=options,headers=headers)
    data_to_display=response.json().get('ResponseCode')
    return HttpResponse(response)
@csrf_exempt
def STKPushDemo(request):    
    response=client.lipanaMpesaOnlineSTKPush()
    return response.json()
@csrf_exempt
def lipaNaMpesaOnline(request):
    url_endpoint="https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers={"Authorization":"Bearer %s" % client.generateMpesaAccessToken()}
    options={    
           "BusinessShortCode":"174379",    
           "Password": client.generateLipanaMpesaPassword(),    
           "Timestamp":"20160216165627",    
           "TransactionType": "CustomerPayBillOnline",    
           "Amount":"1",    
           "PartyA":"254794249057",    
           "PartyB":"174379",    
          "PhoneNumber":"254794249057",    
          "CallBackURL":"https://6677-197-156-190-210.ngrok.io/admin/c2b/confirmation",    
          "AccountReference":"Test",    
          "TransactionDesc":"Test"
        }
    response = requests.post(url_endpoint, json=options, headers=headers)
    print("The Result is:"+str(response))
    

#Get all transactions
@user_is_administrator
def getFareTransactions(request):
    transactions=financialAnalysis.getAllFinances()
    return render(request,"admin/payments.html",{'transactions':transactions})









