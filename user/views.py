from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .serializers import SignupSerializer, UserProfileSerializer
from .models import UserProfile
from .utils import calculate_daily_calories

from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from rest_framework import exceptions
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import ChangePasswordSerializer

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    # Rename 'update' to 'post' to allow POST requests
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Set the new password securely
            self.request.user.set_password(serializer.validated_data['new_password'])
            self.request.user.save()
            
            return Response({
                "status": "success",
                "message": "Password updated successfully"
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # We change the name to 'login_id' to show it accepts both
    username_field = 'username' 

    def validate(self, attrs):
        login_id = attrs.get("username") # SimpleJWT default picks up the first field as 'username'
        password = attrs.get("password")

        # 1. Look for user by Username OR Email
        user = User.objects.filter(Q(username=login_id) | Q(email=login_id)).first()

        # 2. Authenticate the user
        if user:
            # We use the actual username found to authenticate with the password
            authenticated_user = authenticate(username=user.username, password=password)
            
            if authenticated_user:
                if not authenticated_user.is_active:
                    raise exceptions.AuthenticationFailed("User is inactive.")
                
                # 3. Generate tokens using the parent class logic
                refresh = self.get_token(authenticated_user)
                data = {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                }

                # Add custom response data
                data['user_id'] = authenticated_user.username
                data['email'] = authenticated_user.email
                return data
            
        raise exceptions.AuthenticationFailed("No active account found with the given credentials")

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



# Signup View
class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = serializer.save()
            # 'profile' comes from related_name='profile' in UserProfile model
            profile = user.profile 
            
            return Response({
                "status": "success",
                "data": {
                    "user_id": user.username,
                    "daily_calorie_goal": profile.daily_calorie_goal,
                    "bmi": profile.bmi
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Profile View (Retrieve and Update)
class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Return the profile of the logged-in user
        return self.request.user.profile

    def perform_update(self, serializer):
        profile = serializer.save()
        # Re-calculate metrics on update
        h_meters = profile.height_cm / 100
        profile.bmi = round(profile.weight_kg / (h_meters ** 2), 1)
        profile.daily_calorie_goal = calculate_daily_calories(profile)
        profile.save()