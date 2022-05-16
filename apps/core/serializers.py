from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.validators import EmailValidator
from django.shortcuts import get_object_or_404
from rest_framework.fields import CharField, EmailField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.validators import ValidationError

from .models import OneTimeCode
from .utils import get_url
from .validators import PASSWORD_VALIDATORS, six_digits

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "data", "date_joined"]


class RegisterSerializer(ModelSerializer):
    email = EmailField(required=True)
    password = CharField(write_only=True, style={"input_type": "password"})
    next_url = SerializerMethodField()

    def validate_email(self, email):
        EmailValidator()(email)
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use.")
        return email

    def validate_password(self, password):
        for validator in PASSWORD_VALIDATORS:
            validator.validate(password, user=None)
        return password

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data, is_active=False)
        code = OneTimeCode.generate(user).code
        send_mail(
            f"{code} is your code for Vortoj",
            f"Hello,\n\nUse the code {code} to log in.",
            "no-reply@localhost",
            [user.email],
        )
        return user

    def get_next_url(self, obj):
        return f"{get_url(self.context['request']).replace('register', 'verify')}"

    class Meta:
        model = User
        fields = ["email", "password", "next_url"]


class ValidateCodeSerializer(Serializer):
    email = EmailField(required=True)
    code = CharField(required=True)

    def validate_email(self, email):
        EmailValidator()(email)
        if not User.objects.filter(email=email).exists():
            raise ValidationError("This email does not exist.")
        return email

    def validate_code(self, code):
        six_digits(code)
        return code

    def is_valid(self, raise_exception=False):
        super().is_valid(raise_exception=True)
        user = get_object_or_404(User, email=self.data["email"], is_active=False)
        return OneTimeCode.validate(user=user, code=self.data["code"])
