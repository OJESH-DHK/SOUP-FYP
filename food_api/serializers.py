from rest_framework import serializers
from .models import Food
from meal_interaction.models import MealInteraction

class FoodEatSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    food_id = serializers.IntegerField()
    meal_type = serializers.ChoiceField(choices=MealInteraction.MEAL_CHOICES)
    day = serializers.IntegerField(default=1)

class FoodSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['name', 'calories_kcal', 'protein_g', 'carbohydrates_g', 'fat_g']

class MealLogSerializer(serializers.ModelSerializer):
    food_details = FoodSummarySerializer(source='chosen_food', read_only=True)
    class Meta:
        model = MealInteraction
        fields = ['meal_type', 'food_details']