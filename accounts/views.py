from django.http.response import HttpResponse
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
# from rest_framework.authtoken.models import Token
from rest_framework import permissions, authentication
from rest_framework.reverse import reverse
from django.shortcuts import redirect, render
from accounts.handlers.user import AccountHandlerFactory
from accounts.viewsets import AnonViewSet

from .serializers import LoginSerializer, ResetPasswordSerializer, UserSerializer, PasswordRecoverySerializer
from rest_framework import serializers, status
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer

from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.models import AbstractBaseUser
from django.http import JsonResponse, HttpRequest

User: AbstractBaseUser = get_user_model()

class HomeView(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.SessionAuthentication]
    renderer_classes = [TemplateHTMLRenderer]

    def get_home(self, request:HttpRequest) -> HttpResponse: # type: ignore

        handler = AccountHandlerFactory.get("home")
        data, error = handler.get_homepage_data(request.user)

        if error:
            return Response(data, template_name="accounts/home.html", status=status.HTTP_400_BAD_REQUEST)

        return Response(data, template_name="accounts/dashboard.html", status=status.HTTP_200_OK)
    
    def search(self, request:HttpRequest) -> JsonResponse:
        keyword = request.POST.dict().get("coin")
        # print(request.POST.dict())
        results, error = AccountHandlerFactory.get("home").search(keyword)

        if error:
            return JsonResponse({"errors": "Could not process request"}, template_name="accounts/home.html", status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(results, status=status.HTTP_200_OK, safe=False)

class ResgisterUserView(APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request: HttpRequest):
        return render(request, 'accounts/register.html')
    
    def post(self, request: HttpRequest, refferal_code=None) -> Response:
        """User can use a refferal code or link to sign up"""

        data = request.POST.dict()
        if not data:
            data = request.data
            if refferal_code:
                data['refferal_code'] = refferal_code
        
        serializer = UserSerializer(data=data)
        serializer.is_valid()
        if serializer.errors:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        handler = AccountHandlerFactory.get("create_user")
        response, errors = handler.run(serializer.data)

        if errors:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=serializer.data["email"], password=request.data["password"])

        if user:
            login(request, user)
            return redirect(reverse("accounts:home"))
            # return Response(response, template_name="accounts/dashboard.html", status=status.HTTP_201_CREATED)
        
        return Response(400)
    
class LoginView(APIView):

    renderer_classes = [TemplateHTMLRenderer]

    def get(self, request: HttpRequest):
       return render(request, 'accounts/login.html')

    def post(self, request: HttpRequest) -> Response:

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid()
        if serializer.errors:
            return Response(400)
        
        user = authenticate(request, username=serializer.data["email"], password=request.data["password"])
        if not user or not user.is_active:
            return JsonResponse({"detail": "User does not exist"}, status=status.HTTP_401_UNAUTHORIZED) # change the message here
        
        login(request, user)

        response = {
            "user": user
        }

        # return Response(response, template_name="accounts/dashboard.html", status=status.HTTP_200_OK)
        return redirect(reverse("accounts:home"))

class LogoutView(APIView):
    def get(self, request: HttpRequest):
       logout(request) 
       return render("accounts/home.html")

class PasswordRecoveryView(AnonViewSet):

    def forgot_password(self, request: HttpRequest, format=None, **kwargs)-> Response:
        return render(request, 'accounts/recover-password.html')

    def password_reset_validate_email(self, request: HttpRequest, format=None, **kwargs) -> Response:

        serializer = PasswordRecoverySerializer(data=request.data)
        serializer.is_valid()

        if serializer.errors:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # handle the recovery
        handler = AccountHandlerFactory.get("password_recovery")
        _, error = handler.run(data, request=request)

        if error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        
        return JsonResponse({"response": "An email has being sent to your mail, Click on the link to proceed"}, status=status.HTTP_200_OK)
    
    def verify_reset_password(self, request: HttpRequest, uid: str) -> Response:

        handler = AccountHandlerFactory.get("password_recovery")
        response, error = handler.generate_token(uid)

        if error:
            return Response(400)
        
        return Response(response, template_name="accounts/reset-password.html", status=status.HTTP_200_OK)
    
    def reset_password(self, request: HttpRequest, token: str) -> Response:
        data = request.data
        if not data:
            data = request.POST.dict()
        serializer = ResetPasswordSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        handler = AccountHandlerFactory.get("password_recovery")
        response, error = handler.reset_password(serializer.validated_data, token)
        
        if error:
            return JsonResponse({"error": "Reset link is invalid or has expired"}, status=status.HTTP_400_BAD_REQUEST) # change this to include a template with context switch
        
        return Response(template_name="accounts/password-reset-success.html", status=status.HTTP_200_OK)

