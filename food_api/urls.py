from django.urls import path
from .views import HomeScreenView, FoodEatView, FoodSearchView,AnalyticsView

urlpatterns = [
    path('home/', HomeScreenView.as_view(), name='home-screen'),
    path('eat/', FoodEatView.as_view(), name='eat-food'),
    path('search/', FoodSearchView.as_view(), name='food-search'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]