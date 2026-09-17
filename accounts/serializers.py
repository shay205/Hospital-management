from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "first_name", "last_name", "email", "phone", "role", "is_active")
        read_only_fields = ("id",)


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=12)

    class Meta:
        model = User
        fields = ("username", "password", "first_name", "last_name", "email", "phone")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs["username"].strip()
        user = None

        if "@" in username_or_email:
            user = User.objects.filter(email__iexact=username_or_email).first()
            if user is not None:
                user = authenticate(username=user.username, password=attrs["password"])
        else:
            user = authenticate(username=username_or_email, password=attrs["password"])

        if not user or not user.is_active:
            raise serializers.ValidationError("Invalid credentials or inactive account.")
        attrs["user"] = user
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=12)

    def validate_new_password(self, value):
        validate_password(value)
        return value


class ManagedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "email", "phone", "role", "is_active", "is_staff")
        read_only_fields = ("id", "username", "is_staff")
