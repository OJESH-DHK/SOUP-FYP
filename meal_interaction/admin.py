from django.contrib import admin
from .models import MealInteraction

@admin.register(MealInteraction)
class MealInteractionAdmin(admin.ModelAdmin):
    # Show user, what they ate, and when
    list_display = ('user', 'meal_type', 'chosen_food', 'created_at')
    
    # Filter by user and meal type
    list_filter = ('meal_type', 'created_at', 'user')
    
    # Search by user's name or the food's name
    search_fields = ('user__user__username', 'chosen_food__name')
    
    # Make the date read-only (since it's auto-generated)
    readonly_fields = ('created_at', 'updated_at')
    
    # Sort by newest first
    ordering = ('-created_at',)