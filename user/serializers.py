from rest_framework import serializers
from django.contrib.auth.models import User
# Import the choices from models
from .models import (
    UserProfile, GENDER_CHOICES, BODY_CHOICES, 
    GOAL_CHOICES, ACTIVITY_CHOICES, DIET_CHOICES, SPICY_CHOICES
)
from .utils import calculate_daily_calories

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
        fields = ['username', 'password', 'email', 'age', 'height_cm', 'weight_kg', 
                  'gender', 'body_type', 'goal', 'activity', 'diet', 'spicy_pref']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        profile_fields = [
            'age', 'height_cm', 'weight_kg', 'gender', 
            'body_type', 'goal', 'activity', 'diet', 'spicy_pref'
        ]
        profile_data = {field: validated_data.pop(field) for field in profile_fields}

        user = User.objects.create_user(**validated_data)
        bmi = round(profile_data['weight_kg'] / ((profile_data['height_cm'] / 100) ** 2), 1)

        profile = UserProfile.objects.create(user=user, bmi=bmi, **profile_data)
        profile.daily_calorie_goal = calculate_daily_calories(profile)
        profile.save()

        return user