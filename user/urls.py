from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView, MyProfileView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
]