# foods/ml_ranker.py
from meal_interaction.models import MealInteraction
from .ml_ranker_lgbm import rank_foods_for_user as rank_lgbm
from .ml_ranker_lstm import rank_foods_for_user as rank_lstm

MIN_HISTORY = 5  # feel free: 5, 8, 10, or SEQ_LEN

def _history_count(profile) -> int:
    return (
        MealInteraction.objects.filter(user=profile)
        .exclude(chosen_food__isnull=True)
        .count()
    )

def rank_foods_for_user(profile, meal_type: str, foods):
    if _history_count(profile) < MIN_HISTORY:
        return rank_lgbm(profile, meal_type, foods)
    return rank_lstm(profile, meal_type, foods)

