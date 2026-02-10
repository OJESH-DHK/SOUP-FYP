from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .serializers import SignupSerializer, UserProfileSerializer
from .models import UserProfile
from .utils import calculate_daily_calories

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = UserProfile.objects.get(user_id=user.username)
            return Response({
                "status": "success",
                "data": {
                    "user_id": profile.user_id,  
                    "daily_calorie_goal": profile.daily_calorie_goal,
                    "bmi": profile.bmi
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            return Response({"status": "success", "data": UserProfileSerializer(profile).data})
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)

    def patch(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                updated_profile = serializer.save()
                updated_profile.daily_calorie_goal = calculate_daily_calories(updated_profile)
                updated_profile.bmi = round(updated_profile.weight_kg / ((updated_profile.height_cm / 100) ** 2), 1)
                updated_profile.save()
                return Response({"status": "success", "data": UserProfileSerializer(updated_profile).data})
            return Response(serializer.errors, status=400)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=404)