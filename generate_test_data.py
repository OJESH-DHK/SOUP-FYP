import random
import pytz
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from user.models import UserProfile
from food_api.models import Food
from meal_interaction.models import MealInteraction

# 1. SETUP & CLEANUP
KTM = pytz.timezone('Asia/Kathmandu')
DAYS_BACK = 90
today = datetime.now(KTM)

print("🧹 Cleaning up old test data...")
MealInteraction.objects.all().delete()
User.objects.filter(username__in=['loss_tara', 'gain_ram', 'athlete_maya', 'office_hari']).delete()

# 2. DEFINE PERSONAS
PERSONAS = [
    {'username': 'loss_tara', 'goal': 'loss', 'diet': 'veg', 'weight': 85},
    {'username': 'gain_ram', 'goal': 'gain', 'diet': 'nonveg', 'weight': 60},
    {'username': 'athlete_maya', 'goal': 'maintain', 'diet': 'nonveg', 'weight': 65},
    {'username': 'office_hari', 'goal': 'loss', 'diet': 'nonveg', 'weight': 95},
]

def generate_soup_data():
    foods = list(Food.objects.all())
    if not foods:
        print("❌ Error: No foods found in database. Seed foods first!")
        return

    print(f"🚀 Generating 90 days of history for 4 users...")

    for p in PERSONAS:
        # Create User
        user = User.objects.create_user(username=p['username'], password='password123')
        
        # Create Profile
        profile = UserProfile.objects.create(
            user=user,
            gender='male' if p['username'] in ['gain_ram', 'office_hari'] else 'female',
            age=random.randint(22, 40),
            height_cm=random.randint(160, 185),
            weight_kg=p['weight'],
            goal=p['goal'],
            diet=p['diet'],
            daily_calorie_goal=2500 if p['goal'] == 'gain' else 1800
        )

        # Generate 90 Days
        for d in range(DAYS_BACK):
            target_date = today - timedelta(days=DAYS_BACK - d - 1)
            
            for m_type in ['breakfast', 'lunch', 'dinner', 'snack']:
                if m_type == 'snack' and random.random() > 0.5: continue
                
                # Pick 3 options and choose 1
                options = random.sample(foods, min(len(foods), 3))
                chosen = random.choice(options)

                # Set Kathmandu Eating Times
                if m_type == 'breakfast': h = random.randint(7, 9)
                elif m_type == 'lunch': h = random.randint(12, 14)
                elif m_type == 'dinner': h = random.randint(19, 21)
                else: h = random.randint(10, 22)

                meal_dt = target_date.replace(hour=h, minute=random.randint(0, 59), second=0, microsecond=0)

                MealInteraction.objects.create(
                    user=profile,
                    day=d + 1,
                    meal_type=m_type,
                    target_cal=profile.daily_calorie_goal,
                    food_1=options[0] if len(options) > 0 else None,
                    food_2=options[1] if len(options) > 1 else None,
                    food_3=options[2] if len(options) > 2 else None,
                    chosen_food=chosen,
                    created_at=meal_dt
                )

    print("✅ Success! 4 Users created with 90 days of history.")
    print("🔑 Passwords for all: password123")

generate_soup_data()