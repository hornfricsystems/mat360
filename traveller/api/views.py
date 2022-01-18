from rest_framework.decorators import api_view
from rest_framework.response import Response

from traveller.api.serializers import TravellerRegistrationSerializer

@api_view(['POST',])
def travellerRegistrationView(request):
    if request.method == 'POST':
        serializer=TravellerRegistrationSerializer(required=False,data=request.data)
        data={}
        if serializer.is_valid():
            account=serializer.save()
            data['response']='Successfully registered a new Traveller'
        else:
            data=serializer.errors
        return Response(data)
