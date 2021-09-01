from sacco_manager.models import VehicleBookings, Vehicle
import africastalking

from mat360.settings import AFRICAS_TALKING_USERNAME, AFRICAS_TALKING_API_KEY

from mat360admin.models import Mat360SystemUsers

from sacco_manager.models import Route


class ValidationCheck:
    username=AFRICAS_TALKING_USERNAME
    api_key=AFRICAS_TALKING_API_KEY
    def get_bookings_per_ride(self,vnumber):
        vehicleI = Vehicle.objects.get(pk=vnumber)

        total_bookings=VehicleBookings.objects.filter(vehicle=vehicleI).filter(booking_status='active').filter(payment_status=True).count()
        return total_bookings
    #This is the function to prevent double booking.
    def prevent_double_booking(self,user,vehiclen,confirmation_code):
        result=False
        if VehicleBookings.objects.filter(vehicle=vehiclen).filter(booking_status='active').filter(traveller=user).filter(booking_code=confirmation_code).filter(payment_status=True).exists():
            result=True
        else:
            result=False
        return result

    # Function to ensure phone number is in the right format to receive sma.
    def prepare_recipient_number(self, phone):
        prepared = "+254" + phone[1:]
        return prepared


    #This is the function to send SMS;
    def sendSms(self,phone_number,first_name,last_name):
        africastalking.initialize(self.username, self.api_key)
        sms = africastalking.SMS
        # Use the service synchronously
        prepared_number= self.prepare_recipient_number(phone_number)
        response = sms.send("Dear "+first_name+ ' '+last_name+ ".Your ride is full and we are living in 15 minutes.Kindly avail yourself in our stage within the next few minutes.THANK YOU", [prepared_number])
        return response
    def sendMpesaConfirmationCode(self,recipient_number,confirmation_code):
        africastalking.initialize(self.username, self.api_key)
        sms = africastalking.SMS
        # Use the service synchronously
        recipient_phone= self.prepare_recipient_number(recipient_number)
        response = sms.send("Dear traveller your M-PESA confirmation code is:"+str(confirmation_code)+".Use it to complete your booking.",[recipient_phone])
        return response


    def getallroutes(request):
        allRoutes = Route.objects.all()
        route_departureList=[]
        route_detsinationList=[]
        for route in allRoutes:
            if route.departure not in route_departureList:
                route_departureList.append(route.departure)
            route_detsinationList.append(route.destination)
        set_departure=set(route_departureList)
        set_detsination=set(route_detsinationList)
        towns_not_in_departure=list(set_detsination-set_departure)
        all_towns=route_departureList+towns_not_in_departure
        return  all_towns




