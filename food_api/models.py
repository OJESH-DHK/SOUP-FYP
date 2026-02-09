from django.db import models

from core.models import CommonModel

# Create your models here.
class Food(CommonModel):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    food_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=255, blank=True, null=True)

    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)

    calories_kcal = models.FloatField()
    protein_g = models.FloatField(null=True, blank=True)
    carbohydrates_g = models.FloatField(null=True, blank=True)
    fat_g = models.FloatField(null=True, blank=True)
    fiber_g = models.FloatField(null=True, blank=True)
    sugars_g = models.FloatField(null=True, blank=True)
    sodium_mg = models.FloatField(null=True, blank=True)
    cholesterol_mg = models.FloatField(null=True, blank=True)
    water_intake_ml = models.FloatField(null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=["meal_type"]),
            models.Index(fields=["meal_type", "calories_kcal"]),]

    def __str__(self):
        return f"{self.name} ({self.meal_type})"
