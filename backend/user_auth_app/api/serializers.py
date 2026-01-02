from django.contrib.auth.models import User
from rest_framework import serializers

from user_auth_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for reading/writing UserProfile data.
    Note: user fields (first_name, last_name, email) are handled in the view update(),
    because they belong to django.contrib.auth.models.User.
    """

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user",
            "type",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "created_at",
        ]
        read_only_fields = ["id", "user", "created_at"]


class RegistrationSerializer(serializers.Serializer):
    """
    Handles user registration:
    - username, password, repeated_password
    - email
    - type (customer/business)
    """

    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    type = serializers.ChoiceField(choices=UserProfile.USERTYPE_CHOICES)

    def validate_username(self, value: str) -> str:
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username already exists.")
        return value

    def validate_email(self, value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password")
        username = validated_data["username"]
        password = validated_data["password"]
        email = validated_data["email"]
        user_type = validated_data["type"]

        user = User.objects.create_user(username=username, email=email, password=password)
        profile = UserProfile.objects.create(user=user, type=user_type)
        return profile