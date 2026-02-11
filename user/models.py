from django.db import models
from django.contrib.auth.models import User
from core.models import CommonModel

# Define constants for choices
GENDER_CHOICES = [("male", "Male"), ("female", "Female"), ("other", "Other")]
BODY_CHOICES = [("ectomorph", "Ectomorph"), ("mesomorph", "Mesomorph"), ("endomorph", "Endomorph")]
GOAL_CHOICES = [("loss", "Loss"), ("maintain", "Maintain"), ("gain", "Gain")]
ACTIVITY_CHOICES = [("low", "Low"), ("moderate", "Moderate"), ("high", "High")]
DIET_CHOICES = [("veg", "Vegetarian"), ("nonveg", "Non-Vegetarian")]
SPICY_CHOICES = [("low", "Low"), ("medium", "Medium"), ("high", "High")]

class UserProfile(CommonModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    height_cm = models.FloatField(null=True, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    
    body_type = models.CharField(max_length=20, choices=BODY_CHOICES)
    goal = models.CharField(max_length=20, choices=GOAL_CHOICES)
    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    diet = models.CharField(max_length=20, choices=DIET_CHOICES)
    spicy_pref = models.CharField(max_length=20, choices=SPICY_CHOICES)
    daily_calorie_goal = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Profile for {self.user.username}"