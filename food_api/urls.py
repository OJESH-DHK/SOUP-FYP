from django.urls import path
#from .views import FoodRecommendationView, FoodSelectionView
from .views import FoodRecommendationView, FoodEatView, DailySummaryView

urlpatterns = [
    path('recommendations/', FoodRecommendationView.as_view(), name='recommendations'),
    #path('select/', FoodSelectionView.as_view(), name='select-food'),
    path('eat/', FoodEatView.as_view(), name='eat-food'),
    path('summary/', DailySummaryView.as_view(), name='daily-summary'),
]