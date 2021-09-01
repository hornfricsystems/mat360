from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.utils.timezone import now

from mat360admin.models import Mat360SystemUsers


class SaccoRegistrationRequests(models.Model):
    first_name=models.CharField(max_length=20,blank=False,null=False)
    last_name = models.CharField(max_length=20, blank=False, null=False)
    id_number = models.CharField(max_length=20, blank=False, null=False,primary_key=True)
    email_address = models.CharField(max_length=100, blank=False, null=False,unique=True)
    phone_number = models.CharField(max_length=20, blank=False, null=False,unique=True)
    sacco_reg_no = models.CharField(max_length=50, blank=False, null=False)
    sacco_name = models.CharField(max_length=100, blank=False, null=False)
    date_reguested=models.DateTimeField(auto_now_add=now())
    application_status=models.CharField(max_length=15,default='in_progress',blank=False)

    class Meta:
        db_table='sacco_requests'


class SaccoManager(models.Model):
    user = models.OneToOneField(Mat360SystemUsers, on_delete=models.CASCADE,related_name='sacco_manager')
    id_number = models.CharField(max_length=8,primary_key=True)
    date_registered = models.DateTimeField(auto_now=now())

    class Meta:
        db_table='sacco_manager'
class Sacco(models.Model):
    sacco_manager = models.OneToOneField(SaccoManager, on_delete=models.CASCADE,related_name='sacco')
    sacco_reg_no = models.CharField(max_length=50,primary_key=True)
    sacco_name=models.CharField(max_length=100,blank=False,null=False)
    date_registered = models.DateTimeField(auto_now=now())

    class Meta:
        db_table='sacco'




class Route(models.Model):
    departure=models.CharField(max_length=30,blank=False,null=False)
    destination=models.CharField(max_length=30,blank=False,null=False)
    sacco=models.ForeignKey(Sacco,on_delete=models.CASCADE)

    class Meta:
        db_table='routes'

class Driver(models.Model):
    user = models.OneToOneField(Mat360SystemUsers, on_delete=models.CASCADE, related_name='driver')
    id_number = models.CharField(max_length=8, primary_key=True)
    date_registered = models.DateTimeField(auto_now=now())

    class Meta:
        db_table='sacco_driver'

class Vehicle(models.Model):
    sacco=models.ForeignKey(Sacco,on_delete=models.CASCADE,related_name='sacco')
    v_number=models.CharField(max_length=7,primary_key=True)
    capacity=models.IntegerField()
    route=models.ForeignKey(Route,on_delete=models.CASCADE,related_name='route')
    driver=models.OneToOneField(Driver,on_delete=models.CASCADE,related_name='driver')
    date_registered=models.DateTimeField(auto_now=now())

    def activeBookings(self):
        active_bookings=VehicleBookings.objects.filter(vehicle=self.v_number).filter(booking_status='active').count()
        return active_bookings



    class Meta:
        db_table='vehicle'




class StageController(models.Model):
    user=models.OneToOneField(Mat360SystemUsers,on_delete=models.CASCADE,related_name='stagecontroller')
    id_number=models.CharField(max_length=8,primary_key=True)
    station=models.CharField(max_length=50,null=False,blank=False)
    sacco=models.ForeignKey(Sacco,on_delete=models.CASCADE,related_name='sacco_stagecontroller')
    phone_number=models.CharField(max_length=10,unique=True,blank=False)

    class Meta:
        db_table='stage_controller'
class VControl(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name='vcontrol')
    station=models.CharField(max_length=50,blank=False,null=False)
    v_availability_by_driver=models.BooleanField(default=False)
    controller_confirmation_status=models.BooleanField(default=False)
    time_available_by_driver=models.DateTimeField(default=now())
    time_of_confirmation_by_controller=models.DateTimeField(null=True,blank=True)

    class Meta:
        db_table='vehiclecontrol'


class VehicleBookings(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    traveller=models.ForeignKey(Mat360SystemUsers,on_delete=models.CASCADE)
    booking_status=models.CharField(max_length=20,default='active')
    created=models.DateTimeField(auto_now_add=now())
    booking_code=models.PositiveIntegerField(null=False,blank=False)
    payment_status=models.BooleanField(default=False)

    class Meta:
        db_table='vbookings'
#This is the model that will be updated if the vehicle is full;
class VehicleStatus(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    status=models.CharField(max_length=10)
    class Meta:
        db_table='vstatus'
#This is a model to store all transactions
class FareTransactions(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    traveller=models.ForeignKey(Mat360SystemUsers,on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2)
    date_transacted=models.DateTimeField(auto_now_add=now())
    departure_town=models.CharField(max_length=50,blank=False,default='XYZ')
    destination_town=models.CharField(max_length=50,blank=False,default="ZYX")
    class Meta:
        db_table='fareTransactions'
#model that will be used for Sacco Deductions;
class VehicleTrips(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    initial_booking=models.DateTimeField(auto_now_add=now())
    final_booking=models.DateTimeField(blank=True)








