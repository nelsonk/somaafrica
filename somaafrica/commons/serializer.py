from rest_framework.serializers import ModelSerializer

from .models import User, Address, Phone


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class AddressSerializer(ModelSerializer):

    class Meta:
        model = Address
        fields = ['id', 'address']


class PhoneSerializer(ModelSerializer):

    class Meta:
        model = Phone
        fields = '__all__'
