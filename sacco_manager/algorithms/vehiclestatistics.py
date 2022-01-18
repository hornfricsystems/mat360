from mat360admin.models import Payments
from sacco_manager.models import Vehicle
from django.db.models import Sum
class VehicleStatistics:
    def __init__(self,vNumber):
        self.vNumber=vNumber
    def getGrossEarnings(self):
        gross_earnings=Payments.objects.filter(bill_refnumber=self.vNumber).aggregate(Sum('transaction_amount'))
        formatted_amount=gross_earnings['transaction_amount__sum']
        return formatted_amount
    def getVehicleDetails(self):
        vehicleDetails=Vehicle.objects.get(pk=self.vNumber)
        return vehicleDetails

