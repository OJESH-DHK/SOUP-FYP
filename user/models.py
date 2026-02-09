from django.db import models

from core.models import CommonModel

# Create your models here.
class UserProfile(CommonModel):
    BODY_CHOICES = [
        ("ectomorph", "Ectomorph"),
        ("mesomorph", "Mesomorph"),
        ("endomorph", "Endomorph"),
    ]

    GOAL_CHOICES = [
        ("loss", "Loss"),
        ("maintain", "Maintain"),
        ("gain", "Gain"),
    ]

    ACTIVITY_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
    ]

    DIET_CHOICES = [
        ("veg", "Vegetarian"),
        ("nonveg", "Non-Vegetarian"),
    ]

    SPICY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
    ]

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    user_id = models.CharField(max_length=50, unique=True)

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



    class Meta:
        indexes = [
            models.Index(fields=["goal"]),
            models.Index(fields=["diet"]),
            models.Index(fields=["body_type"]),
        ]

    def __str__(self):
        return self.user_id
