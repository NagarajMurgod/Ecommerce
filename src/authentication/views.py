from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from .serializers import CreateUserSerializer,UserLoginSerializer,CustomeTokenRefreshSerializer, LogoutRequestSerializer
from rest_framework import status
from common.helpers import validation_error_handler
from authentication.models import User
from .helpers import AuthHelper
from django.conf import settings
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth.hashers import check_password  # authenticate method can also be used to check the password, but it make new db query to fethc user object , to availd it manually chcking the password
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class SignupView(APIView):  
    serializer_class = CreateUserSerializer

    def post(self, request, *args,**kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:

            return Response({
                'status': 'error',
                'message' : validation_error_handler(serializer.errors),
                'payload':{
                    "errors":serializer.errors
                }
            },status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        email = validated_data["email"]
        password = validated_data["password"]

        existing_user = User.objects.filter(email=email).first()

        if existing_user is not None:
            print(existing_user.is_active)
            if existing_user.is_active is False:
                existing_user.set_password(password)
                existing_user.save()
                user = existing_user
            else:
                return Response({
                    "status":"error",
                    "message":"Account with this email address already exists",
                    "payload":{}
                },status=status.HTTP_400_BAD_REQUEST)
        else:
            username = AuthHelper.create_username(email=email)
            user = User.objects.create_user(
                username=username,
                is_active = False,
                **validated_data
            )
        serializer_data = self.serializer_class(user).data
        context_data = {
            "host": settings.FRONTEND_HOST,
            "uid": urlsafe_base64_encode(force_bytes(user.id)),
            "token": account_activation_token.make_token(user=user),
            "protocol": settings.FRONTEND_PROTOCOL
        }
        print(context_data)

        # subject = "Verify Email for your account verfication on ShowNow"
        # template = "auth/email/verify_email.html"  
        # context_data = {
        #     "host" : settings.FRONTEND_HOST,
        #     "uid" : urlsafe_base64_encode(force_bytes(user.id)),
        #     "token" : account_activation_token.make_token(user=user),
        #     'protocol': settings.FRONTEND_PROTOCOL
        # }

        return Response({
            "status": "success",
            "message": "Sent the account verification link to your email address",
            "payload": {
                **serializer_data,
                "tokens": AuthHelper.get_tokens_for_user(user)
            }
        })


class ActivateAccountView(APIView):
    def get(self,request,uidb64,token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except Exception as e:
            user = None
            print(e)
        
        if user and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return Response({
                "status" : "success",
                "message" : "successfuly verified",
                "payload" : {}
            },status=status.HTTP_200_OK)
        else:
            return Response({
                "status" : "error",
                "message": "invalid ativation link",
                "payload" : {}
            },status=status.HTTP_403_FORBIDDEN)


class LoginView(APIView):

    serializer_class = UserLoginSerializer


    def post(self, request, *args,**kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:

            return Response({
                'status': 'error',
                'message' : validation_error_handler(serializer.errors),
                'payload':{
                    "errors":serializer.errors
                }
            },status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        username_or_email = validated_data["username_or_email"]
        password = validated_data["password"]

        user = (User.objects.filter(email=username_or_email).first() or User.objects.filter(username=username_or_email).first())

        if user is not None:
            validated_password = check_password(
                password, user.password
            )
        
            if validated_password:
                if user.is_active is False:
                    return Response({
                        "status" : "error",
                        "message" : "user account is not active , please verify your email"
                    },status=HTTP_403_FORBIDDEN)
                
                serializer_data = self.serializer_class(
                    user , context = {"request":request}
                )

                return Response({
                    "status" : "success",
                    "message" : "login successfull",
                    "payload" : {
                        **serializer_data.data,
                        "token" : AuthHelper.get_tokens_for_user(user)
                    }
                },status=status.HTTP_200_OK)
            
            else:
                return Response({
                    "status" : "error",
                    "message" : "No user found",
                    "payload" : {}
                },status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({
                'status' : "error",
                "message" : "no user found",
                "payload" : {}
            },status=status.HTTP_404_NOT_FOUND)



class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomeTokenRefreshSerializer


class UserLogoutView(APIView):
    serializer_class = LogoutRequestSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args,**kwargs):
        request_data = request.data
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid() is False:

            return Response({
                'status': 'error',
                'message' : validation_error_handler(serializer.errors),
                'payload':{
                    "errors":serializer.errors
                }
            },status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        try:
            if validated_data.get("all"):
                for token in OutstandingToken.objects.filter(user=request.user):
                    _,_ = BlacklistedToken.objects.get_or_create(token=token)

                    return Response({
                        "status" : "success",
                        "message": "succesfully logged out from all the devices"
                    },status=status.HTTP_200_OK)
            
            refresh_token = validated_data.get('refresh')

            token = RefreshToken(token=refresh_token)
            token.blacklist()
            return Response({
                "status" : "success",
                "message": "succesfully logged out from  the devices"
            },status=status.HTTP_200_OK)
        
            
            
        except TokenError:
            return Response({
                "detail" : "token is blaklisted",
                "code" : "token_not valid"

            },status=status.HTTP_401_UNAUTHORIZED)




