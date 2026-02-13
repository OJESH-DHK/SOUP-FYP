# foods/ml_ranker_lstm.py
import os
import numpy as np
import torch
import torch.nn as nn
import joblib
from django.conf import settings
from meal_interaction.models import MealInteraction

MODEL_PATH = os.path.join(settings.BASE_DIR, "ml_models", "lstm_ranker.pt")
META_PATH  = os.path.join(settings.BASE_DIR, "ml_models", "lstm_meta.pkl")

# Must match training
SEQ_LEN = 10
EMB_DIM = 32
HIDDEN_DIM = 128

CAT_COLS = ["goal", "body_type", "activity", "diet", "spicy_pref", "food_meal_type"]
NUM_COLS = ["bmi", "calories_kcal", "protein_g", "carbs_g", "fat_g", "abs_cal_diff"]

_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
_model = None
_meta = None


class LSTMRanker(nn.Module):
    def __init__(self, food_vocab_size: int, cat_cardinalities: list[int]):
        super().__init__()
        self.food_emb = nn.Embedding(food_vocab_size + 1, EMB_DIM)
        self.cat_emb = nn.ModuleList([nn.Embedding(n, 8) for n in cat_cardinalities])
        self.lstm = nn.LSTM(EMB_DIM, HIDDEN_DIM, batch_first=True)

        in_dim = HIDDEN_DIM + EMB_DIM + len(NUM_COLS) + len(CAT_COLS) * 8
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 1),
        )

    def forward(self, hist, x_num, x_cat, food_id):
        hist_emb = self.food_emb(hist)          # (B,T,E)
        _, (h, _) = self.lstm(hist_emb)
        user_vec = h[-1]                        # (B,H)

        food_vec = self.food_emb(food_id)       # (B,E)

        cat_vecs = [emb(x_cat[:, i]) for i, emb in enumerate(self.cat_emb)]
        cat_vec = torch.cat(cat_vecs, dim=1)    # (B, cat*8)

        x = torch.cat([user_vec, food_vec, x_num, cat_vec], dim=1)
        logits = self.mlp(x).squeeze(-1)        # (B,)
        return logits


def _load_once():
    global _model, _meta
    if _model is not None and _meta is not None:
        return

    _meta = joblib.load(META_PATH)

    encoders = _meta["encoders"]     # dict of LabelEncoders (goal/body_type/.../food_meal_type)
    food_le  = _meta["food_le"]      # LabelEncoder for food_id
    scaler   = _meta["scaler"]       # StandardScaler for NUM_COLS

    # Cardinalities must match training encoders
    cat_cardinalities = [len(encoders[c].classes_) for c in CAT_COLS]
    food_vocab_size = len(food_le.classes_)

    model = LSTMRanker(food_vocab_size=food_vocab_size, cat_cardinalities=cat_cardinalities)
    state = torch.load(MODEL_PATH, map_location=_DEVICE)
    model.load_state_dict(state)
    model.to(_DEVICE)
    model.eval()

    _model = model


def _safe_le_transform(le, value: str) -> int:
    # minimal safe handling for unseen category
    value = str(value)
    if value in le.classes_:
        return int(le.transform([value])[0])
    return 0


def _build_user_history(profile):
    """
    Returns list of original food_ids (Food.food_id) of chosen foods (oldest->newest), padded to SEQ_LEN.
    """
    qs = (
        MealInteraction.objects.filter(user=profile)
        .exclude(chosen_food__isnull=True)
        .order_by("-id")  # use -created_at if you have it
        .values_list("chosen_food__food_id", flat=True)[:SEQ_LEN]
    )
    hist = list(reversed(list(qs)))  # oldest->newest
    if len(hist) < SEQ_LEN:
        hist = [0] * (SEQ_LEN - len(hist)) + hist
    return hist


def rank_foods_for_user(profile, meal_type: str, foods):
    """
    foods: iterable of Food objects
    returns: list of (food_db_pk, score) sorted desc
    """
    _load_once()
    print("used lstm")
    encoders = _meta["encoders"]
    scaler = _meta["scaler"]
    food_le = _meta["food_le"]

    # mapping original food_id -> embedding index (LabelEncoder index)
    food_class_map = {int(x): i for i, x in enumerate(food_le.classes_)}

    # user categorical
    x_user = [
        _safe_le_transform(encoders["goal"], profile.goal),
        _safe_le_transform(encoders["body_type"], profile.body_type),
        _safe_le_transform(encoders["activity"], profile.activity),
        _safe_le_transform(encoders["diet"], profile.diet),
        _safe_le_transform(encoders["spicy_pref"], profile.spicy_pref),
    ]
    bmi = float(getattr(profile, "bmi", 0.0) or 0.0)

    # history encoded into embedding space
    hist_raw = _build_user_history(profile)
    hist_enc = [food_class_map.get(int(fid), 0) for fid in hist_raw]

    foods = list(foods)
    B = len(foods)
    if B == 0:
        return []

    hist = torch.tensor([hist_enc] * B, dtype=torch.long)

    x_cat = []
    x_num = []
    food_idx = []
    db_ids = []

    for f in foods:
        db_ids.append(f.id)
        # candidate food embedding index uses original Food.food_id
        food_idx.append(food_class_map.get(int(f.food_id), 0))

        food_meal = getattr(f, "meal_type", meal_type)
        x_cat.append(x_user + [_safe_le_transform(encoders["food_meal_type"], food_meal)])

        cal = float(getattr(f, "calories_kcal", 0.0) or 0.0)
        prot = float(getattr(f, "protein_g", 0.0) or 0.0)
        carbs = float(getattr(f, "carbs_g", 0.0) or 0.0)
        fat = float(getattr(f, "fat_g", 0.0) or 0.0)

        # If you store per-meal target in MealInteraction, you can pass it in; minimal fallback:
        target_cal = float(getattr(profile, "daily_calorie_goal", 2000) or 2000) / 3.0
        abs_diff = abs(target_cal - cal)

        x_num.append([bmi, cal, prot, carbs, fat, abs_diff])

    x_cat = torch.tensor(np.asarray(x_cat, dtype=np.int64))
    x_num = scaler.transform(np.asarray(x_num, dtype=np.float32))
    x_num = torch.tensor(x_num, dtype=torch.float32)
    food_idx = torch.tensor(np.asarray(food_idx, dtype=np.int64))

    hist = hist.to(_DEVICE)
    x_cat = x_cat.to(_DEVICE)
    x_num = x_num.to(_DEVICE)
    food_idx = food_idx.to(_DEVICE)

    with torch.no_grad():
        logits = _model(hist, x_num, x_cat, food_idx)
        probs = torch.sigmoid(logits).detach().cpu().numpy()

    ranked = sorted(zip(db_ids, probs.tolist()), key=lambda x: x[1], reverse=True)
    return ranked
