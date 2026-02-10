from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Food
from user.models import UserProfile
from meal_interaction.models import MealInteraction
from .serializers import FoodEatSerializer, MealLogSerializer

class FoodRecommendationView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.query_params.get('user_id')
        meal_type = request.query_params.get('meal_type', 'breakfast').lower()
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        daily_target = getattr(profile, 'daily_calorie_goal', 2000)
        split_map = {"breakfast": 0.3, "lunch": 0.4, "dinner": 0.3, "snack": 0.1}
        target_cal = daily_target * split_map.get(meal_type, 0.3)
        candidates = Food.objects.filter(
            meal_type=meal_type,
            calories_kcal__range=(target_cal * 0.85, target_cal * 1.15)
        )
        if candidates.count() < 3:
            candidates = Food.objects.filter(meal_type=meal_type)
        sorted_foods = sorted(candidates, key=lambda x: abs(x.calories_kcal - target_cal))[:3]
        interaction, _ = MealInteraction.objects.update_or_create(
            user=profile, day=1, meal_type=meal_type,
            defaults={
                'target_cal': target_cal,
                'food_1': sorted_foods[0] if len(sorted_foods) > 0 else None,
                'food_2': sorted_foods[1] if len(sorted_foods) > 1 else None,
                'food_3': sorted_foods[2] if len(sorted_foods) > 2 else None,
            }
        )
        return Response({
            "user_id": user_id,
            "meal_type": meal_type,
            "meal_target": round(target_cal, 1),
            "recommendations": [{"food_id": f.food_id, "name": f.name, "kcal": f.calories_kcal} for f in sorted_foods]
        })

class FoodEatView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = FoodEatSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                interaction = MealInteraction.objects.get(
                    user__user_id=data['user_id'],
                    day=data['day'],
                    meal_type=data['meal_type'].lower()
                )
                food_item = Food.objects.get(food_id=data['food_id'])
                interaction.chosen_food = food_item
                interaction.save()
                return Response({"status": "success", "message": f"Logged {food_item.name}"})
            except (MealInteraction.DoesNotExist, Food.DoesNotExist):
                return Response({"error": "Interaction or Food not found"}, status=404)
        return Response(serializer.errors, status=400)

class DailySummaryView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user_id = request.query_params.get('user_id')
        day = request.query_params.get('day', 1)
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            interactions = MealInteraction.objects.filter(user=profile, day=day).exclude(chosen_food__isnull=True)
            total_eaten = sum(item.chosen_food.calories_kcal for item in interactions)
            logged_meals = MealLogSerializer(interactions, many=True).data
            return Response({
                "user_id": user_id,
                "daily_goal": profile.daily_calorie_goal,
                "total_eaten": round(total_eaten, 1),
                "remaining": round(profile.daily_calorie_goal - total_eaten, 1),
                "history": logged_meals
            })
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=404)