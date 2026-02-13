from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.users_list, name='users_list'),
    path('users/<uuid:user_id>/', views.user_detail, name='user_detail'),  # Changed to uuid
    path('foods/', views.foods_list, name='foods_list'),
    path('analytics/', views.analytics, name='analytics'),
]