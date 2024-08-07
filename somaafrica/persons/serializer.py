from rest_framework.serializers import ModelSerializer

from somaafrica.commons.serializer import UserSerializer, PhoneSerializer
from somaafrica.commons.serializer import AddressSerializer
from .models import Person


class PersonSerializer(ModelSerializer):
    user = UserSerializer()
    phone = PhoneSerializer(required=False)
    address = AddressSerializer(required=False)

    class Meta:
        model = Person
        fields = '__all__'
