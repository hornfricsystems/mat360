from django.contrib.auth.models import AbstractUser
from django.db import models




class Mat360SystemUsers(AbstractUser):
    is_customer=models.BooleanField(default=False)
    is_driver=models.BooleanField(default=False)
    is_saccomanager=models.BooleanField(default=False)
    is_stagecontroller=models.BooleanField(default=False)


    class Meta:
        db_table='mat360systemusers'
'''
This is the table to hold the payments of the MPESA Transactions.
'''
class Payments(models.Model):
    #This will help us get the number of the user paying.
    user=models.ForeignKey(Mat360SystemUsers,on_delete=models.CASCADE)
    transaction_type=models.CharField(max_length=10,blank=False,null=False)
    transaction_id=models.CharField(max_length=10,blank=False,unique=True)
    transaction_time=models.DateTimeField()
    transaction_amount=models.DecimalField(max_digits=10,decimal_places=2)
    business_shortcode=models.CharField(max_length=6,blank=False,null=False)
    bill_refnumber=models.ForeignKey("sacco_manager.Vehicle",on_delete=models.CASCADE)
    invoice_number=models.CharField(max_length=5,null=True,blank=True)
    msisdn=models.CharField(max_length=12,blank=False,null=False)
    first_name=models.CharField(max_length=20,blank=False,null=False)
    middle_name=models.CharField(max_length=20,blank=True,null=True)
    last_name=models.CharField(max_length=20,blank=False,null=False)
    booking_code=models.PositiveIntegerField()

    class Meta:
        db_table="ride_payments"

    
        





