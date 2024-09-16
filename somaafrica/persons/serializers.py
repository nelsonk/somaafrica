from django.contrib.auth.models import Permission
from rest_framework import serializers

from .models import User, Address, Phone, Person, Group


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True)  # passwd not returned

    class Meta:
        model = User
        exclude = ['password']


class GroupSerializer(serializers.ModelSerializer):
    group_members = UserSerializer(many=True, read_only=True)
    permissions = serializers.ReadOnlyField(source="group_permissions")

    class Meta:
        model = Group
        fields = '__all__'


class UserSignupSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    def validate(self, data):
        # pdb.set_trace()
        if not data.get("username") and not data.get("email"):
            raise serializers.ValidationError("Username or Email required")

        if data.get("password1") != data.get("password2"):
            raise serializers.ValidationError("Password mismatch")

        return data


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'


class PhoneSerializer(serializers.ModelSerializer):

    class Meta:
        model = Phone
        fields = '__all__'


class PersonSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    phone = PhoneSerializer(required=False)
    address = AddressSerializer(required=False)

    class Meta:
        model = Person
        fields = '__all__'
