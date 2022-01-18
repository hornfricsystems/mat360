import json

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views.generic.base import TemplateView

from mat360.settings import EMAIL_HOST_USER
from mat360admin.core.decorators import  saccoManagerRequired
from mat360admin.models import Mat360SystemUsers
from mat360admin.core.company_finances import CompanyFinancesController
from sacco_manager.algorithms.tokens import account_activation_token
from sacco_manager.forms import SaccoRequestRegistrationForm, VehicleRegistrationForm, StageControllerRegistrationForm
from sacco_manager.models import Sacco, Driver, Vehicle, StageController, Route

from sacco_manager.algorithms.algo import FilterClass
from sacco_manager.algorithms.vehiclestatistics import VehicleStatistics

decorators=[saccoManagerRequired,login_required(login_url='admin:admin-login')]
#This is a function to save sacco registration requests and send an email to the administrator.
def save_sacco_registration_requests(request):
    if request.method == 'POST':
        form=SaccoRequestRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            subject="New Sacco Registration Request"
            message="Dear Administrator,you have a new sacco registration request.Kindly check the submitted details to either approve or reject"
            recipient='kilimoc@gmail.com'
            send_mail(subject,message,EMAIL_HOST_USER,[recipient],fail_silently=True)
            messages.success(request,"Your application has been saved successfully and email has been send to mat360 for review.It will take less than 24 hours before they can get back to you.")
            form=SaccoRequestRegistrationForm()
        else:
            messages.error(request,"Your form was submitted with errors.Ensure you have entered correct values.")
    else:
        form=SaccoRequestRegistrationForm()
    return render(request,'new_sacco_registration_request.html',{'form':form})

@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def sacco_manager_dashboard(request):
    cfO=CompanyFinancesController(request.user.sacco_manager.sacco.sacco_reg_no)
    total_vehicles=cfO.getSaccoSummaryData()
    financialcustomer_summary=cfO.getSaccoTotalFinacialandCustomerSummary()
    context={
    'company_summary':total_vehicles,
    'payments':financialcustomer_summary,
    'customer_count':len(financialcustomer_summary['customers']),
    'travellers':financialcustomer_summary['customers'],

    }
    return render(request,'sacco_manager/index.html',context)
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def vehicle_statistics(request):

    cfO=CompanyFinancesController(request.user.sacco_manager.sacco.sacco_reg_no)
    total_vehicles=cfO.getSaccoSummaryData()
    financialcustomer_summary=cfO.getSaccoTotalFinacialandCustomerSummary()
    context={
    'company_summary':total_vehicles,
    'payments':0,
    'customer_count':len(financialcustomer_summary['customers']),
    'travellers':financialcustomer_summary['customers'],

    }
    return render(request,'sacco_manager/vehicle_stats.html',context)
#This is used to save details of a new vehicle for the specific sacco into the database.
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def new_vehicle_registration(request):
    sacco_pk = Sacco.objects.get(pk=request.user.sacco_manager.sacco.sacco_reg_no)
    all_routes = sacco_pk.route_set.all()
    if request.method == 'POST':
        form=VehicleRegistrationForm(request.POST)
        if form.is_valid():
            #Register the driver to the database too.
            #.First as a user
            user = Mat360SystemUsers()
            user.first_name = form.cleaned_data['first_name']
            user.last_name =  form.cleaned_data['last_name']
            user.username =  form.cleaned_data['phone_number']
            user.email =  form.cleaned_data['email_address']
            user.password = make_password( form.cleaned_data['id_number'])
            user.is_driver=True
            user.save()
            #2.As a Driver.
            driver=Driver()
            driver_user=Mat360SystemUsers.objects.get(username=form.cleaned_data['phone_number'])
            driver.user=driver_user
            driver.id_number=form.cleaned_data['id_number']
            driver.save()


            fs = form.save(commit=False)
            sacco = Sacco.objects.get(pk=request.user.sacco_manager.sacco.sacco_reg_no)
            route = Route.objects.filter(pk=request.POST['vehicle_route']).get(sacco=sacco_pk)
            #route=VehicleRoute.objects.get(pk=route_o.id)

            v_driver=Driver.objects.get(pk=form.cleaned_data['id_number'])
            fs.sacco = sacco
            fs.route = route
            fs.driver=v_driver
            fs.save()
            messages.success(request,"Vehicle has been successfully registered")
            form = VehicleRegistrationForm()
    else:
        form = VehicleRegistrationForm()

    return render(request,'sacco_manager/new_vehicle.html',{'form':form,'all_routes':all_routes})


#Return all fleet of a sacco
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def get_fleet(request):
    vehicles=Vehicle.objects.filter(sacco=request.user.sacco_manager.sacco.sacco_reg_no).select_related('driver').select_related('route')
    return render(request,'sacco_manager/our_fleet.html',{'vehicles':vehicles})
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def register_stage_controller(request):
    #Get all registered stage controllers;
    sacco_r = Sacco.objects.get(pk=request.user.sacco_manager.sacco.sacco_reg_no)
    stage_controllers=StageController.objects.filter(sacco=sacco_r)
    if request.method == 'POST':
        form=StageControllerRegistrationForm(request.POST)

        if form.is_valid():
            user = Mat360SystemUsers()
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.username = form.cleaned_data['phone_number']
            user.email = form.cleaned_data['email']
            user.is_stagecontroller=True
            user.password = make_password(form.cleaned_data['id_number'])
            user.save()

            # 2.As a Stage Controller
            stagec=StageController()
            stagec_user = Mat360SystemUsers.objects.get(username=form.cleaned_data['phone_number'])

            stagec.user = stagec_user
            stagec.sacco=sacco_r
            stagec.id_number = form.cleaned_data['id_number']
            stagec.phone_number=form.cleaned_data['phone_number']
            stagec.station = form.cleaned_data['station']
            stagec.save()
            #Email confirmation link
            current_site=get_current_site(request)
            mail_subject="Please Activate your Account"
            message_mail=render_to_string('sacco_manager/account_activation.html',{
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token,
            })

            subject = "STAGE CONTROLLER REGISTRATION"
            message="Dear "+form.cleaned_data['first_name']+ " "+ form.cleaned_data['last_name'] +",you have been registered as  "+sacco_r.sacco_name.upper()+" Stage Controller managing "+form.cleaned_data['station'].upper()+" Sation.Your Login Credentials are shown below \n Username:\t"+form.cleaned_data['phone_number']+"\n Password:\t"+form.cleaned_data['id_number']
            recipient = form.cleaned_data['email']
            send_mail(subject, message, EMAIL_HOST_USER, [recipient], fail_silently=True)
            send_mail(mail_subject, message_mail, EMAIL_HOST_USER, [recipient], fail_silently=True)

            messages.success(request,'Stage Controller has been registered successfully and email confirmation send with log in details')
            form=StageControllerRegistrationForm()


    else:
        form = StageControllerRegistrationForm(request.POST)
    return  render(request,'sacco_manager/new_stage_controller.html',{'form':form,'controllers':stage_controllers})





#Final function to register route
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def register_vehicle_route(request):
    saccoInstance = Sacco.objects.get(pk=request.user.sacco_manager.sacco.sacco_reg_no)
    all_routes = saccoInstance.route_set.all()
    #Get instance of class
    filterI=FilterClass()
    if request.method == 'POST':
        sdeparture=request.POST['departure']
        sdestination=request.POST['destination']

        if filterI.prepare_town_search(sdeparture,sdestination):
            if Route.objects.filter(Q(sacco=saccoInstance), Q(departure=sdeparture.upper()),Q(destination=sdestination.upper())).exists():
                messages.error(request, 'The route is already registered in your sacco')
            else:
                routeI = Route()
                routeI.departure = sdeparture.upper()
                routeI.destination = sdestination.upper()
                routeI.sacco = saccoInstance
                routeI.save()
                messages.success(request, 'Vehicle Route has been recorded successfully.')
            #Now check for entry else
        else:
            if Route.objects.filter(Q(sacco=saccoInstance), Q(departure=sdestination.upper()),Q(destination=sdeparture.upper())).exists():
                messages.error(request, 'The route is already registered in your sacco')
            else:
                routeI = Route()
                routeI.departure = sdestination.upper()
                routeI.destination = sdeparture.upper()
                routeI.sacco = saccoInstance
                routeI.save()
                messages.success(request, 'Vehicle Route has been recorded successfully.')

    return render(request, 'sacco_manager/routes.html', {'all_routes': all_routes})
@login_required(login_url='admin:admin-login')
@saccoManagerRequired
def sacco_settings(request):
    return render(request,'sacco_manager/sacco_settings.html')






def logout_view(request):
    logout(request)
    return redirect('mat360admin:admin-login')
@method_decorator(decorators,name='dispatch')
class SaccoFinancesPage(TemplateView):
    template_name='sacco_manager/sacco_finances.html'
    def get_context_data(self, **kwargs):
        context=super(SaccoFinancesPage,self).get_context_data(**kwargs)
        cFinance = CompanyFinancesController(self.request.user.sacco_manager.sacco.sacco_reg_no)
        finance_distribution={}
        finance_distribution['total_amount']=cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum']['transaction_amount__sum']
        finance_distribution['sacco_finances']=cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum']['transaction_amount__sum']*10/100
        finance_distribution['owner_finances']=cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum']['transaction_amount__sum']*90/100

        context['finance_summary']=finance_distribution
        return context

@method_decorator(decorators,name='dispatch')
class CurrentBalanceDistribution(TemplateView):
    template_name='sacco_manager/current_balance_distribution.html'
    def get_context_data(self, **kwargs):
        context=super(CurrentBalanceDistribution, self).get_context_data(**kwargs)
        cFinance = CompanyFinancesController(self.request.user.sacco_manager.sacco.sacco_reg_no)
        finance_distribution = {}
        finance_distribution['total_amount'] = cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum'][
            'transaction_amount__sum']
        finance_distribution['sacco_finances'] = cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum'][
                                                     'transaction_amount__sum'] * 10 / 100
        finance_distribution['owner_finances'] = cFinance.getSaccoTotalFinacialandCustomerSummary()['payments_sum'][
                                                     'transaction_amount__sum'] * 90 / 100
        all_rides=cFinance.getSaccoTotalFinacialandCustomerSummary()['customers']

        context['finance_summary'] = finance_distribution
        context['vehicle_individual_contributions']=all_rides
        return context

'''
AJAX BASED FUNCTIONS
'''
@saccoManagerRequired
@login_required(login_url='admin:admin-login')
def getVehicleStatistics(request):
    vehicleNumber = request.GET.get('vNumber', None)
    #Create Object
    vStats=VehicleStatistics("KBA001A")
    gross_earnings=vStats.getGrossEarnings()
    result_set=[]
    result_set.append({"vNumber":gross_earnings})
    return HttpResponse(json.dumps(result_set), content_type='application/json')






