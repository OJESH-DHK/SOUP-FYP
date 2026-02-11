import csv
import os
from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import User
from user.models import UserProfile
from food_api.models import Food
from meal_interaction.models import MealInteraction

class Command(BaseCommand):
    help = 'High-speed sync of CSV data with Database'

    def handle(self, *args, **kwargs):
        base_path = 'data'
        self.stdout.write(self.style.WARNING("🚀 Starting high-speed sync..."))

        # 1. Sync Food (Relatively small, update_or_create is fine)
        self.sync_food(os.path.join(base_path, 'foods.csv'))
        
        # 2. Sync Users
        self.sync_users(os.path.join(base_path, 'users.csv'))
        
        # 3. Sync Interactions (The Big One)
        self.sync_interactions(os.path.join(base_path, 'meal_interactions.csv'))

        self.stdout.write(self.style.SUCCESS('✅ Successfully synced all data!'))

    def sync_food(self, path):
        self.stdout.write("🍎 Syncing Food...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Food.objects.update_or_create(
                    food_id=int(row['food_id']),
                    defaults={
                        'name': row['Food_Item'],
                        'category': row['Category'],
                        'calories_kcal': float(row['Calories (kcal)']),
                        'meal_type': row['Meal_Type'].lower(),
                        'protein_g': float(row.get('Protein (g)', 0) or 0),
                        'carbohydrates_g': float(row.get('Carbohydrates (g)', 0) or 0),
                        'fat_g': float(row.get('Fat (g)', 0) or 0),
                    }
                )

    def sync_users(self, path):
        self.stdout.write("👤 Syncing Users...")
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                user, _ = User.objects.get_or_create(
                    username=row['user_id'],
                    defaults={'email': f"{row['user_id']}@example.com"}
                )
                if _:
                    user.set_password('password123')
                    user.save()

                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={
                        'gender': row['gender'].lower(),
                        'age': int(row['age']),
                        'height_cm': float(row['height_cm']),
                        'weight_kg': float(row['weight_kg']),
                        'bmi': float(row.get('bmi', 0)),
                    }
                )

    def sync_interactions(self, path):
        self.stdout.write("⚡ Syncing Interactions (Bulk Mode)...")
        # Pre-load to avoid thousands of DB queries
        food_cache = {f.food_id: f for f in Food.objects.all()}
        user_cache = {up.user.username: up for up in UserProfile.objects.select_related('user').all()}
        
        interactions_to_create = []
        batch_size = 5000 
        
        # Clear existing to avoid duplicates if using bulk_create
        MealInteraction.objects.all().delete()

        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                profile = user_cache.get(row['user_id'])
                if not profile: continue

                # Memory-only creation
                interaction = MealInteraction(
                    user=profile,
                    day=int(row['day']),
                    meal_type=row['meal_type'].lower(),
                    target_cal=float(row['target_cal']),
                    food_1=food_cache.get(int(row['food_1'])) if row['food_1'] else None,
                    food_2=food_cache.get(int(row['food_2'])) if row['food_2'] else None,
                    food_3=food_cache.get(int(row['food_3'])) if row['food_3'] else None,
                    chosen_food=food_cache.get(int(row['chosen_food'])) if row['chosen_food'] else None,
                )
                interactions_to_create.append(interaction)

                if len(interactions_to_create) >= batch_size:
                    MealInteraction.objects.bulk_create(interactions_to_create)
                    interactions_to_create = []
            
            if interactions_to_create:
                MealInteraction.objects.bulk_create(interactions_to_create)