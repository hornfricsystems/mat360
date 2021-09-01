import base64
import json
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import requests
from requests.auth import HTTPBasicAuth
from mat360.settings import CONSUMER_KEY,CONSUMER_SECRET,BUSINESS_SHORTCODE
from mat360admin.models import Payments


class MpesaClient:
    consumer_key = CONSUMER_KEY
    consumer_secret = CONSUMER_SECRET
    lipaTime = datetime.now().strftime("%Y%m%d%H%M%S")
    businessShortCode = BUSINESS_SHORTCODE
    phoneNumber="254794249057"


    def generateMpesaAccessToken(self):
        authorization_endpoint_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        response = requests.get(authorization_endpoint_url, auth=HTTPBasicAuth(self.consumer_key, self.consumer_secret))
        mpesa_access_token_content = json.loads(response.text)
        generated_access_token = mpesa_access_token_content['access_token']
        return generated_access_token

    def generateLipanaMpesaPassword(self):
        '''
        This is a combination of the lipa time and the business Shortcode
        and the online passKey provided by Daraja api'''

        businessShortCode = "174379"
        passKey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        data_to_encode = self.lipaTime + businessShortCode + passKey
        encoded_data = base64.b64encode(data_to_encode.encode())
        decoded_online_password = encoded_data.decode('utf-8')
        return decoded_online_password

    # This is the function to enable people trigger stk push on their mobile phones.
    def lipanaMpesaOnlineSTKPush(self):
        endpoint_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": "Bearer %s" % self.generateMpesaAccessToken()}
        request = {
            "BusinessShortCode": self.businessShortCode,
            "Password": self.generateLipanaMpesaPassword(),
            "Timestamp": self.lipaTime,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": 1,
            "PartyA": self.phoneNumber,
            "PartyB": self.businessShortCode,
            "PhoneNumber": self.phoneNumber,
            "CallBackURL": "https://215f-154-122-111-129.ngrok.io/admin/c2b/confirmation",
            "AccountReference": "Cornelius",
            "TransactionDesc": "Fare",
        }
        response = requests.post(endpoint_url, json=request, headers=headers)
        return response
    @csrf_exempt
    def simulateTransaction(self,amount,vehicle):
          api_URL="https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate"
          headers = {"Authorization": "Bearer %s" % self.generateMpesaAccessToken()}
          options={
            "CommandID":"CustomerPayBillOnline",
            "Amount":amount,
            #Should be replaced with the usernumber
            "Msisdn":254708374149,
            "BillRefNumber":vehicle,
            "ShortCode":"600997",
            }
          response=requests.post(api_URL,json=options,headers=headers)
          results=response.json().get('ResponseCode')
          return results


'''
*****COMPANY FINANCIALS*******
'''
class Mat360FinancialAnalysis:
    def getAllFinances(self):
        all_finances=Payments.objects.all()
        return all_finances