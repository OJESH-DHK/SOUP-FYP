from django.contrib import admin
from .models import Food

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    # What columns to show in the list view
    list_display = ('name', 'meal_type', 'calories_kcal', 'protein_g', 'category')
    
    # Add a search bar for names and categories
    search_fields = ('name', 'category')
    
    # Add a sidebar filter for meal types and categories
    list_filter = ('meal_type', 'category')
    
    # Organize the detail view into sections
    fieldsets = (
        ("Basic Info", {
            "fields": ("food_id", "name", "category", "meal_type")
        }),
        ("Nutritional Values", {
            "fields": ("calories_kcal", "protein_g", "carbohydrates_g", "fat_g", "fiber_g")
        }),
        ("Additional Data", {
            "fields": ("sodium_mg", "cholesterol_mg", "water_intake_ml"),
            "classes": ("collapse",) # Hides this section by default
        }),
    )