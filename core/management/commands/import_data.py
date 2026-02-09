import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from user.models import UserProfile
from food_api.models import Food
from meal_interaction.models import MealInteraction

class Command(BaseCommand):
    help = 'Syncs CSV data with Database'

    def handle(self, *args, **kwargs):
        # Your data folder is in the root
        base_path = 'data'
        
        self.stdout.write(self.style.WARNING("Starting sync..."))

        # 1. Sync Food (File name matches your 'ls' output: foods.csv)
        self.sync_food(os.path.join(base_path, 'foods.csv'))
        
        # 2. Sync Users
        self.sync_users(os.path.join(base_path, 'users.csv'))
        
        # 3. Sync Interactions
        self.sync_interactions(os.path.join(base_path, 'meal_interactions.csv'))

        self.stdout.write(self.style.SUCCESS('Successfully synced all data!'))

    def sync_food(self, path):
        self.stdout.write("Syncing Food...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Note: keys match your CSV column names exactly
                Food.objects.update_or_create(
                    food_id=row['food_id'],
                    defaults={
                        'name': row['Food_Item'],
                        'category': row['Category'],
                        'calories_kcal': float(row['Calories (kcal)']),
                        'meal_type': row['Meal_Type'].lower(),
                        'protein_g': float(row.get('Protein (g)', 0) or 0),
                        'carbohydrates_g': float(row.get('Carbohydrates (g)', 0) or 0),
                        'fat_g': float(row.get('Fat (g)', 0) or 0),
                        'fiber_g': float(row.get('Fiber (g)', 0) or 0),
                        'sugars_g': float(row.get('Sugars (g)', 0) or 0),
                        'sodium_mg': float(row.get('Sodium (mg)', 0) or 0),
                        'cholesterol_mg': float(row.get('Cholesterol (mg)', 0) or 0),
                        'water_intake_ml': float(row.get('Water_Intake (ml)', 0) or 0),
                    }
                )

    def sync_users(self, path):
        self.stdout.write("Syncing Users...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                UserProfile.objects.update_or_create(
                    user_id=row['user_id'],
                    defaults={
                        'gender': row['gender'],
                        'age': int(row['age']),
                        'height_cm': float(row['height_cm']),
                        'weight_kg': float(row['weight_kg']),
                        'body_type': row['body_type'],
                        'goal': row['goal'],
                        'activity': row['activity'],
                        'diet': row['diet'],
                        'spicy_pref': row['spicy_pref'],
                        'bmi': float(row['bmi']),
                    }
                )

    def sync_interactions(self, path):
        self.stdout.write("Syncing Interactions...")
        # Caching for performance with 200k rows
        food_cache = {f.food_id: f for f in Food.objects.all()}
        user_cache = {u.user_id: u for u in UserProfile.objects.all()}

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            with transaction.atomic():
                for row in reader:
                    user_obj = user_cache.get(row['user_id'])
                    if not user_obj:
                        continue

                    MealInteraction.objects.update_or_create(
                        user=user_obj,
                        day=int(row['day']),
                        meal_type=row['meal_type'],
                        defaults={
                            'target_cal': float(row['target_cal']),
                            'food_1': food_cache.get(int(row['food_1'])),
                            'food_2': food_cache.get(int(row['food_2'])),
                            'food_3': food_cache.get(int(row['food_3'])),
                            'chosen_food': food_cache.get(int(row['chosen_food'])),
                        }
                    )