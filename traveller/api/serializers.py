from rest_framework import serializers

from mat360admin.models import Mat360SystemUsers


class TravellerRegistrationSerializer(serializers.ModelSerializer):
    password2=serializers.CharField(style={'input_type':'password'},write_only=True)
    class Meta:
        model=Mat360SystemUsers
        fields=['first_name','last_name','username','is_customer','password','password2']
        extra_kwargs={
            'password':{'write_only':True},
        }
    def save(self):
        traveller=Mat360SystemUsers(
            first_name=self.validated_data['first_name'],
            last_name=self.validated_data['last_name'],
            username=self.validated_data['username'],
            is_customer=True,
        )
        password=self.validated_data['password']
        password2=self.validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'password':'Password do not match'})
        traveller.set_password(password)
        traveller.save()