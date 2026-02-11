from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import SignupSerializer, UserProfileSerializer
from .utils import calculate_daily_calories

class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Automatically get the profile for the logged-in JWT user
        return self.request.user.profile

    def perform_update(self, serializer):
        profile = serializer.save()
        # Re-calculate metrics after update
        profile.bmi = round(profile.weight_kg / ((profile.height_cm / 100) ** 2), 1)
        profile.daily_calorie_goal = calculate_daily_calories(profile)
        profile.save()