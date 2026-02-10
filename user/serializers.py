from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile
from .utils import calculate_daily_calories

class SignupSerializer(serializers.ModelSerializer):
    # These fields are for the UserProfile calculation logic
    age = serializers.IntegerField(write_only=True)
    height_cm = serializers.FloatField(write_only=True)
    weight_kg = serializers.FloatField(write_only=True)
    gender = serializers.ChoiceField(choices=UserProfile.GENDER_CHOICES, write_only=True)
    body_type = serializers.ChoiceField(choices=UserProfile.BODY_CHOICES, write_only=True)
    goal = serializers.ChoiceField(choices=UserProfile.GOAL_CHOICES, write_only=True)
    activity = serializers.ChoiceField(choices=UserProfile.ACTIVITY_CHOICES, write_only=True)
    diet = serializers.ChoiceField(choices=UserProfile.DIET_CHOICES, write_only=True)
    spicy_pref = serializers.ChoiceField(choices=UserProfile.SPICY_CHOICES, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'age', 'height_cm', 'weight_kg', 
                  'gender', 'body_type', 'goal', 'activity', 'diet', 'spicy_pref']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # 1. Separate profile data from user data
        profile_data = {
            'age': validated_data.pop('age'),
            'height_cm': validated_data.pop('height_cm'),
            'weight_kg': validated_data.pop('weight_kg'),
            'gender': validated_data.pop('gender'),
            'body_type': validated_data.pop('body_type'),
            'goal': validated_data.pop('goal'),
            'activity': validated_data.pop('activity'),
            'diet': validated_data.pop('diet'),
            'spicy_pref': validated_data.pop('spicy_pref'),
        }

        # 2. Create the base Auth User
        user = User.objects.create_user(**validated_data)

        # 3. Calculate BMI
        bmi = round(profile_data['weight_kg'] / ((profile_data['height_cm'] / 100) ** 2), 1)

        # 4. Create the UserProfile
        profile = UserProfile.objects.create(
            user_id=user.username,
            bmi=bmi,
            **profile_data
        )

        # 5. Run your math logic from utils.py and save it
        profile.daily_calorie_goal = calculate_daily_calories(profile)
        profile.save()

        return user
    
from rest_framework import serializers
from .models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        # This returns every field defined in your models.py
        fields = '__all__'