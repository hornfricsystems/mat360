from rest_framework.decorators import api_view
from rest_framework.response import Response

from traveller.api.serializers import TravellerRegistrationSerializer

@api_view(['POST',])
def travellerRegistrationView(request):
    if request.method == 'POST':
        serializer=TravellerRegistrationSerializer(required=False,data=request.data)
        data=""
        if serializer.is_valid():
            account=serializer.save()
            data='You have Successfully registered as a new Traveller'
        else:
            response=serializer.errors
            data=response['username'][0]

        return Response(data)
