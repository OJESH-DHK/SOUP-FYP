from django.urls import path,include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import SignupView, MyProfileView, MyTokenObtainPairView
urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', MyProfileView.as_view(), name='my-profile'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]