from rest_framework import serializers
from authentication.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import EmailValidator
from rest_framework_simplejwt.serializers import TokenRefreshSerializer



class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'email',
            'password'
        ]

        extra_kwargs = {
            "password" : {"write_only":True},
            "email" : {
                "validators" : [EmailValidator]
            }
        }


    def validate_password(self,value):
        validate_password(value)
        return value
    
    def validate_email(self,value):
        return value.lower()


class UserLoginSerializer(serializers.ModelSerializer):
    username_or_email = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User
        fields = (
            "username_or_email",
            "email",
            "password",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser"
        )

        read_only_fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "date_joined",
            "is_active",
            "is_superuser"
        ]

        extra_kwargs = {
            "password" : { "write_only" : True}
        }
    
    def validate_username_or_email(self,value):
        return value.lower()


class CustomeTokenRefreshSerializer(TokenRefreshSerializer):
    pass
        
    
class LogoutRequestSerializer(serializers.Serializer):
    all = serializers.BooleanField(required=False)
    refresh = serializers.CharField(required=False)

    def validate(self, attrs):
        all = attrs.get('all')
        refresh = attrs.get('refresh')
        if not all and not refresh:

            raise serializers.ValidationError({
                "refresh" : "if logout from all device then provide all prameter with value true else refresh token"
            })
        return super().validate(attrs)