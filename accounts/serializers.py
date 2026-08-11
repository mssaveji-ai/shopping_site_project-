from rest_framework import serializers
from .models import User
from django.utils.crypto import get_random_string
from utiles.send_custom_mail import send_email

class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['email', 'password','confirm_password']
        extra_kwargs = {'password':{'write_only': True}}
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        new_user = User(
                email=validated_data['email'],
                email_active_code=get_random_string(60),
                is_active = False,
            )
        new_user.set_password(validated_data['password'])
        new_user.save()
        send_email('account_activation',new_user.email,{'user':new_user},'email/activate_account.html')
        return new_user
    

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model= User
        fields = ['email','first_name','last_name','image','about_user', 'address']
        read_only_fields = ['email']
        
        