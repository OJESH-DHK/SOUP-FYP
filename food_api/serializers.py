from rest_framework import serializers
from .models import Food
from meal_interaction.models import MealInteraction

class FoodSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['food_id', 'name', 'calories_kcal', 'protein_g', 'carbohydrates_g', 'fat_g', 'category']

class MealHistorySerializer(serializers.ModelSerializer):
    food_name = serializers.ReadOnlyField(source='chosen_food.name')
    calories = serializers.ReadOnlyField(source='chosen_food.calories_kcal')

    class Meta:
        model = MealInteraction
        fields = ['meal_type', 'food_name', 'calories']

class FoodEatSerializer(serializers.Serializer):
    food_id = serializers.IntegerField()
    meal_type = serializers.CharField()
    day = serializers.IntegerField(default=1)

from rest_framework import serializers
from .models import Food
from meal_interaction.models import MealInteraction

class FoodSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['food_id', 'name', 'calories_kcal', 'protein_g', 'carbohydrates_g', 'fat_g', 'category']

class MealHistorySerializer(serializers.ModelSerializer):
    food_name = serializers.ReadOnlyField(source='chosen_food.name')
    calories = serializers.ReadOnlyField(source='chosen_food.calories_kcal')
    # Using the date from created_at (inherited from CommonModel)
    date = serializers.DateTimeField(source='created_at', format="%Y-%m-%d")

    class Meta:
        model = MealInteraction
        fields = ['meal_type', 'food_name', 'calories', 'date']