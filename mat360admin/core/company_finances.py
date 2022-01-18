from sacco_manager.models import Sacco,Vehicle,Route
from mat360admin.models import Payments
from django.db.models import Sum
class CompanyFinancesController:
	"""This is the class that will have core operations of the company."""
	def __init__(self, organization_code):		
		self.organization_code = organization_code
	#Functions to get all the company finances.
	def getCompanyFinances():
		pass
	#The function to get all the company customer details;
	def getCompanyCustomers():
		pass
	#The function to get the company customer complains
	def getCompanyCustomerComplains():
		pass
	def getSaccoSummaryData(self):
		summary={}
		sacco=Sacco.objects.get(pk=self.organization_code)
		all_vehicles=Vehicle.objects.filter(sacco=sacco).count()
		#Get total routes
		all_routes=Route.objects.filter(sacco=sacco).count()
		summary['all_vehicles']=all_vehicles
		summary['all_routes']=all_routes
		return summary
	def getSaccoTotalFinacialandCustomerSummary(self):	
		financialcustomer_summary={}
		get_all_vehicle_payments=Payments.objects.filter(bill_refnumber__sacco= self.organization_code).aggregate(Sum('transaction_amount'))
		customer_count=Payments.objects.filter(bill_refnumber__sacco= self.organization_code).distinct()
		financialcustomer_summary['payments_sum']=get_all_vehicle_payments
		financialcustomer_summary['customers']=customer_count
		return financialcustomer_summary
	#This is the function to get total number of rides




		
		