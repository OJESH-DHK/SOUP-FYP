from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SignupSerializer

class SignupView(generics.CreateAPIView):
    """
    Handles User Registration and UserProfile creation.
    Calculates the Daily Calorie Goal automatically.
    """
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Retrieve the profile to return the calculated data
            profile = user.user_profile  # Assuming related_name='user_profile' or default
            
            return Response({
                "status": "success",
                "message": "User and Profile created successfully",
                "data": {
                    "user_id": user.username,
                    "email": user.email,
                    "daily_calorie_goal": profile.daily_calorie_goal,
                    "bmi": profile.bmi
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)