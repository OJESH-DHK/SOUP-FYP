def calculate_daily_calories(profile):
    """
    Uses the Mifflin-St Jeor Equation to calculate daily calorie needs.
    """
    # 1. Calculate Basal Metabolic Rate (BMR)
    if profile.gender == "male":
        bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) + 5
    else:
        bmr = (10 * profile.weight_kg) + (6.25 * profile.height_cm) - (5 * profile.age) - 161

    # 2. Activity Multipliers
    activity_map = {
        "low": 1.2,        # Sedentary
        "moderate": 1.55,   # Active 3-5 days/week
        "high": 1.725      # Very active
    }
    tdee = bmr * activity_map.get(profile.activity, 1.2)

    # 3. Adjust for the Goal
    # Loss: -500 kcal (approx 0.5kg/week)
    # Gain: +500 kcal
    if profile.goal == "loss":
        daily_goal = tdee - 500
    elif profile.goal == "gain":
        daily_goal = tdee + 500
    else:
        daily_goal = tdee

    # 4. Body Type Fine-Tuning (Professional touch)
    # Endomorphs often have slower metabolisms; Ectomorphs higher.
    if profile.body_type == "endomorph":
        daily_goal -= 100
    elif profile.body_type == "ectomorph":
        daily_goal += 100

    return round(daily_goal, 0)