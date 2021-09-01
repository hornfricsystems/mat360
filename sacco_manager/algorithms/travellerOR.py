from sacco_manager.models import FareTransactions
from mat360admin.models import Payments
from django.db.models import Sum


class TravellerOperations:
   def get_my_rides(self,user):
       my_rides=Payments.objects.filter(user=user)
       return  my_rides
   def getTotalTransportExpense(self,user):
   		total_expense=Payments.objects.filter(user=user).aggregate(Sum('transaction_amount'))
   		return total_expense

