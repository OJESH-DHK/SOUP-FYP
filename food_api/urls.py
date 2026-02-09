from django.urls import path
from .views import FoodRecommendationView

urlpatterns = [
    path('recommendations/', FoodRecommendationView.as_view(), name='food-recommendations'),
]