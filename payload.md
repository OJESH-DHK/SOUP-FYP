🍎 SOUP-FYP API Technical Documentation
Base URL: http://127.0.0.1:8000/api/v1

Auth Type: JWT Bearer Token

🔐 1. Authentication Flow
A. Signup (New User)
Endpoint: POST /user/signup/

Payload:

JSON
{
    "username": "ojesh_dev",
    "password": "securepassword123",
    "email": "ojesh@example.com",
    "age": 22,
    "height_cm": 175.0,
    "weight_kg": 75.0,
    "gender": "male",
    "body_type": "mesomorph",
    "goal": "loss",
    "activity": "moderate",
    "diet": "nonveg",
    "spicy_pref": "medium"
}
B. Login (Get Tokens)
Endpoint: POST /user/login/

Payload:

JSON
{
    "username": "ojesh_dev",
    "password": "securepassword123"
}
Response: Use the access token for all subsequent requests in the Header: Authorization: Bearer <token>.

C. Refresh Token
Endpoint: POST /user/token/refresh/

Payload:

JSON
{
    "refresh": "PASTE_REFRESH_TOKEN_HERE"
}
🥗 2. Food & Recommendation Flow
A. Get Recommendations
Endpoint: GET /food/recommendations/

Params: user_id (str), meal_type (breakfast/lunch/dinner/snack)

Endpoint Example: /food/recommendations/?user_id=ojesh_dev&meal_type=breakfast

Payload: None

B. Log Eaten Food
Endpoint: POST /food/eat/

Payload:

JSON
{
    "user_id": "ojesh_dev",
    "food_id": 204,
    "meal_type": "breakfast",
    "day": 1
}
C. Daily Summary (Dashboard)
Endpoint: GET /food/summary/

Params: user_id (str), day (int)

Endpoint Example: /food/summary/?user_id=ojesh_dev&day=1

Payload: None

👤 3. Profile Management
A. Get Profile Details
Endpoint: GET /user/profile/<user_id>/

Payload: None

B. Update Profile (Triggers Goal Recalculation)
Endpoint: PATCH /user/profile/<user_id>/

Description: Use this to change weight or activity. The system will automatically update the daily_calorie_goal.

Payload:

JSON
{
    "weight_kg": 72.0,
    "activity": "high",
    "goal": "maintain"
}
🛠 4. Developer Notes
Header: Every request (except Signup/Login) must include Authorization: Bearer <access_token>.

Meal Split: Calories are partitioned as Breakfast (30%), Lunch (40%), Dinner (30%), Snacks (10%).

Recalculation: Any PATCH to weight or height automatically updates the BMI and Calories in the database.
