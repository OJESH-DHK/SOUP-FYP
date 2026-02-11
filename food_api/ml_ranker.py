import os
import pandas as pd
import joblib
import lightgbm as lgb
from django.conf import settings

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models", "food_ranker_lgbm_best.txt")
META_PATH  = os.path.join(settings.BASE_DIR, "ml_models", "food_ranker_lgbm_best_meta.pkl")

_model = None
_meta = None

def get_ranker():
    global _model, _meta
    if _model is None or _meta is None:
        _model = lgb.Booster(model_file=MODEL_PATH)
        _meta = joblib.load(META_PATH)
    return _model, _meta


def rank_foods_for_user(profile, meal_type: str, foods):
    """
    foods: iterable of Food (or dicts) containing the features you trained on.
    returns: list of (food_id, score) sorted desc
    """
    model, meta = get_ranker()
    feature_cols = meta["feature_columns"]
    cat_cols = meta.get("categorical_columns", [])

    # Build rows: ONE ROW PER CANDIDATE FOOD
    rows = []
    for f in foods:
        rows.append({
            # ---- user/profile features ----
            "goal": profile.goal,
            "body_type": profile.body_type,
            "activity": profile.activity,
            "diet": profile.diet,
            "spicy_pref": profile.spicy_pref,

            # ---- request context ----
            "meal_type": meal_type,

            # ---- food features (MUST match training columns you used) ----
            "food_meal_type": f.meal_type,
            # include whatever numeric features existed in ranker_train.csv:
            "calories_kcal": getattr(f, "calories_kcal", 0) or 0,

            # keep id for mapping
            "_food_id": f.id,
        })

    df = pd.DataFrame(rows)

    # Ensure all training columns exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    # Keep only training columns in correct order
    X = df[feature_cols].copy()

    # Apply categorical dtype
    for c in cat_cols:
        if c in X.columns:
            X[c] = X[c].astype("category")

    scores = model.predict(X)
    ranked = sorted(zip(df["_food_id"].tolist(), scores), key=lambda x: x[1], reverse=True)
    return ranked
