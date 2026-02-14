from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    UserProfile, GENDER_CHOICES, BODY_CHOICES, 
    GOAL_CHOICES, ACTIVITY_CHOICES, DIET_CHOICES, SPICY_CHOICES
)
from .utils import calculate_daily_calories
from rest_framework import serializers
from django.contrib.auth.models import User

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        return data

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = UserProfile
        fields = [
            'username', 'email', 'gender', 'age', 'height_cm', 'weight_kg', 
            'bmi', 'body_type', 'goal', 'activity', 'diet', 
            'spicy_pref', 'daily_calorie_goal'
        ]

class SignupSerializer(serializers.ModelSerializer):
    # Profile fields defined as write_only so they are accepted in the POST request
    age = serializers.IntegerField(write_only=True)
    height_cm = serializers.FloatField(write_only=True)
    weight_kg = serializers.FloatField(write_only=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, write_only=True)
    body_type = serializers.ChoiceField(choices=BODY_CHOICES, write_only=True)
    goal = serializers.ChoiceField(choices=GOAL_CHOICES, write_only=True)
    activity = serializers.ChoiceField(choices=ACTIVITY_CHOICES, write_only=True)
    diet = serializers.ChoiceField(choices=DIET_CHOICES, write_only=True)
    spicy_pref = serializers.ChoiceField(choices=SPICY_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'email', 'age', 'height_cm', 'weight_kg', 
            'gender', 'body_type', 'goal', 'activity', 'diet', 'spicy_pref'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Extract profile fields so they aren't passed to User.objects.create_user
        profile_fields = [
            'age', 'height_cm', 'weight_kg', 'gender', 
            'body_type', 'goal', 'activity', 'diet', 'spicy_pref'
        ]
        profile_data = {field: validated_data.pop(field) for field in profile_fields}

        # 1. Create the User instance
        user = User.objects.create_user(**validated_data)
        
        # 2. Calculate BMI
        h_meters = profile_data['height_cm'] / 100
        bmi_val = round(profile_data['weight_kg'] / (h_meters ** 2), 1)

        # 3. Create the UserProfile linked to this user
        profile = UserProfile.objects.create(
            user=user, 
            bmi=bmi_val, 
            **profile_data
        )
        
        # 4. Calculate and save initial calorie goal
        profile.daily_calorie_goal = calculate_daily_calories(profile)
        profile.save()

        return user