from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from basket import serializers
from .forms import RegisterForm, LoginForm
from .models import User
from django.utils.crypto import get_random_string
from django.contrib.auth import login, logout
from django.http import Http404
from utiles.send_custom_mail import send_email
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer, ProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated


class RegisterAPI(APIView):
    permission_classes= [AllowAny,]

    def post(self,request):
        srz_data = RegisterSerializer(data=request.data)
        if srz_data.is_valid():
            srz_data.save()
            return Response({"message":"User registered successfully. Check your email to activate the account."}, status=status.HTTP_201_CREATED)
        return Response(srz_data.errors, status=status.HTTP_400_BAD_REQUEST)

class Register(View):
    def get(self,request):
        register_form = RegisterForm()
        return render(request,'accounts/register.html',{'register_form':register_form})
    def post(self,request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            email = register_form.cleaned_data.get('email')
            password = register_form.cleaned_data.get('password')
            same_email = User.objects.filter(email__iexact=email).exists()
            if same_email:
                register_form.add_error('email','This email address is already registered')
            else:
                new_user = User(
                    email=email,
                    email_active_code=get_random_string(60),
                    is_active = False,
                )
                new_user.set_password(password)
                new_user.save()
                send_email('account_activation',new_user.email,{'user':new_user},'email/activate_account.html')
                return redirect(reverse('home-page'))
        return render(request,'accounts/register.html',{'register_form':register_form})


class ActivateAccountAPI(APIView):
    permission_classes= [AllowAny,]

    def get(self, request, activation_code):
        user = User.objects.filter(email_active_code__iexact = activation_code).first()
        if user:
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(60)
                user.save()
                return Response({'message':'Account activated successfully'},status=status.HTTP_200_OK)
            else:
                return Response({'message':'Account is already active'},status=status.HTTP_200_OK)
        else:
            return Response({'message':'Activation code is invalid'}, status=status.HTTP_404_NOT_FOUND)

class ActivateAccount(View):
    def get(self,request,activation_code):
        user = User.objects.filter(email_active_code__iexact = activation_code).first()
        if user:
            if not user.is_active:
                user.is_active = True
                user.email_active_code = get_random_string(60)
                user.save()
                return redirect(reverse('home-page'))
            else:
                return redirect(reverse('home-page'))
        raise Http404


class Login(View):
    def get(self,request):
        login_form = LoginForm()
        return render (request,'accounts/login.html',{'login_form':login_form})
    
    def post(self,request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            form_email = login_form.cleaned_data.get('email')
            user = User.objects.filter(email__iexact=form_email).first()
            if user:
                if user.is_active:
                    form_password = login_form.cleaned_data.get('password')
                    is_password_correct = user.check_password(form_password)
                    if is_password_correct:
                        login(request, user)
                        return redirect(reverse('home-page'))
                    else:
                        login_form.add_error(None,'The username or password is incorrect')
                else:
                    login_form.add_error(None,'The username or password is incorrect')
            else:
                login_form.add_error(None,'The username or password is incorrect')   

        return render (request,'accounts/login.html',{'login_form':login_form})

class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'message':'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST) 

        user = User.objects.filter(email__iexact=email).first()
        if not user:
            return Response({'message':'Email or password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)  
        
        if not user.is_active:
            return Response({'message':'The account is not active.'}, status=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            return Response({'message':'Email or password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
          
        login(request, user)
        return Response({'message':'Logged in successfully'}, status=status.HTTP_200_OK)
    


class LogoutAPI(APIView):

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message":"Louged out successfully"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"message":"Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
      
class Logout(View):
    def get(self,request):
        logout(request)
        return redirect (reverse('login-form'))


# Create your views here.
class ProfileAPI(APIView):

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response (serializer.data)
    
    def patch(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response (serializer.data)
    
        return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
