from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import Food
from meal_interaction.models import MealInteraction
from .serializers import FoodSummarySerializer, FoodEatSerializer, MealHistorySerializer
from .ml_ranker import rank_foods_for_user
import random

class HomeScreenView(APIView):
    permission_classes = [IsAuthenticated]

    def get_current_meal_type(self):
        hour = datetime.now().hour
        if 5 <= hour < 11: return "breakfast"
        elif 11 <= hour < 17: return "lunch"
        elif 17 <= hour < 23: return "dinner"
        else: return "snack"

    def get(self, request):
        profile = request.user.profile
        # Get selected tab from URL (e.g., ?type=snack), default to current time
        requested_type = request.query_params.get('type', self.get_current_meal_type()).lower()
        
        # 1. Calculate Daily Progress
        interactions = MealInteraction.objects.filter(
            user=profile, day=1
        ).exclude(chosen_food__isnull=True)
        
        total_eaten = interactions.aggregate(total=Sum('chosen_food__calories_kcal'))['total'] or 0
        daily_target = profile.daily_calorie_goal or 2000
        
        candidates = list(
            Food.objects.filter(meal_type=requested_type)
                .exclude(calories_kcal__lt=50)  # optional: avoid condiments issue
                .only("id", "meal_type", "calories_kcal")  # include fields used for ML
                [:800]  # limit candidates
        )

        # 3) Rank candidates using ML, then pick top 4
        ranked = rank_foods_for_user(profile, requested_type, candidates)
        # 4) Take top 30, then random 4 from those
        TOP_K = 30
        PICK_N = 4

        top_k_ids = [fid for fid, _ in ranked[:TOP_K]]
        picked_ids = random.sample(top_k_ids, k=min(PICK_N, len(top_k_ids)))

        # 5) Keep the display order consistent with ML ranking (optional but nice)
        picked_set = set(picked_ids)
        picked_ids = [fid for fid, _ in ranked if fid in picked_set][:PICK_N]

        # 6) Map ids -> objects (no extra DB query)
        food_map = {f.id: f for f in candidates}
        suggestions = [food_map[i] for i in picked_ids if i in food_map]

        
        # 3. Get History (What the user already ate today)
        history = MealInteraction.objects.filter(user=profile, day=1).exclude(chosen_food__isnull=True)

        return Response({
            "daily_progress": {
                "consumed": round(total_eaten, 0),
                "goal": round(daily_target, 0),
                "remaining": round(max(0, daily_target - total_eaten), 0),
                "percentage": round((total_eaten / daily_target) * 100, 1) if daily_target > 0 else 0
            },
            "selected_meal": {
                "label": requested_type.capitalize(),
                "active_now": self.get_current_meal_type(),
                "is_viewing_current": requested_type == self.get_current_meal_type(),
                "suggestions": FoodSummarySerializer(suggestions, many=True).data
            },
            "meal_history": MealHistorySerializer(history, many=True).data
        })

class FoodEatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = FoodEatSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            profile = request.user.profile
            
            try:
                food_item = Food.objects.get(food_id=data['food_id'])
                
                # FIX: Provide target_cal from profile to satisfy the Database constraint
                interaction, created = MealInteraction.objects.get_or_create(
                    user=profile,
                    day=data.get('day', 1),
                    meal_type=data['meal_type'].lower(),
                    defaults={'target_cal': profile.daily_calorie_goal or 2000}
                )
                
                # Update the food choice
                interaction.chosen_food = food_item
                interaction.save()
                
                return Response({
                    "status": "success", 
                    "message": f"Logged {food_item.name}",
                    "consumed_now": food_item.calories_kcal
                })
            except Food.DoesNotExist:
                return Response({"error": "Food ID not found"}, status=404)
        return Response(serializer.errors, status=400)

class FoodSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"results": []})
        
        # Search by name or category
        foods = Food.objects.filter(
            Q(name__icontains=query) | Q(category__icontains=query)
        )[:15] 
        
        serializer = FoodSummarySerializer(foods, many=True)
        return Response({
            "query": query,
            "results": serializer.data
        })
from django.utils import timezone
from datetime import timedelta

class AnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = request.user.profile
        # Get period from URL: /analytics/?period=weekly or ?period=monthly
        period = request.query_params.get('period', 'weekly')
        
        days_back = 7 if period == 'weekly' else 30
        start_date = timezone.now() - timedelta(days=days_back)

        # Filter interactions over the time period
        # Note: This assumes you add a 'created_at' field to your MealInteraction model
        history = MealInteraction.objects.filter(
            user=profile, 
            created_at__gte=start_date
        ).values('created_at__date').annotate(
            total_calories=Sum('chosen_food__calories_kcal')
        ).order_by('created_at__date')

        return Response({
            "period": period,
            "goal": profile.daily_calorie_goal,
            "data": list(history)
        })