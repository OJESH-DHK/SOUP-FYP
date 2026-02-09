from rest_framework.views import APIView
from rest_framework.response import Response
from user.models import UserProfile
from .models import Food
from meal_interaction.models import MealInteraction

class FoodRecommendationView(APIView):
    def get(self, request):
        user_id = request.query_params.get('user_id')
        meal_type = request.query_params.get('meal_type')

        # 1. Identify User
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # 2. Calculate Target Calories (Fixed logic from Path A instructions)
        daily_map = {"loss": 1800, "maintain": 2200, "gain": 2600}
        total_daily = daily_map.get(profile.goal, 2200)

        split_map = {"breakfast": 0.30, "lunch": 0.40, "dinner": 0.30, "snack": 0.10}
        multiplier = split_map.get(meal_type.lower(), 0.30)
        
        target_cal = total_daily * multiplier
        
        # 3. Filter Foods (Target ± 15%)
        candidates = Food.objects.filter(
            meal_type=meal_type,
            calories_kcal__range=(target_cal * 0.85, target_cal * 1.15)
        )

        # 4. Select Top 3 closest to target
        sorted_candidates = sorted(
            candidates, 
            key=lambda x: abs(x.calories_kcal - target_cal)
        )[:3]

        if not sorted_candidates:
            return Response({"error": "No foods found in calorie range"}, status=404)

        # 5. Save/Update Interaction (This fixes the 500 Error)
        interaction, created = MealInteraction.objects.update_or_create(
            user=profile,
            day=1, # Hardcoded for now per instructions
            meal_type=meal_type,
            defaults={
                'target_cal': target_cal,
                'food_1': sorted_candidates[0] if len(sorted_candidates) > 0 else None,
                'food_2': sorted_candidates[1] if len(sorted_candidates) > 1 else None,
                'food_3': sorted_candidates[2] if len(sorted_candidates) > 2 else None,
            }
        )

        # 6. Response
        return Response({
            "user_id": user_id,
            "meal_type": meal_type,
            "target_cal": round(target_cal, 2),
            "recommendations": [
                {"food_id": f.food_id, "name": f.name, "calories": f.calories_kcal} 
                for f in sorted_candidates
            ]
        })