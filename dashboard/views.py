from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from user.models import UserProfile
from food_api.models import Food
from meal_interaction.models import MealInteraction


@staff_member_required
def dashboard_home(request):
    """Main dashboard with overview statistics"""
    from django.db.models import Prefetch
    
    # Time periods
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User Statistics
    total_users = UserProfile.objects.count()
    new_users_week = UserProfile.objects.filter(created_at__gte=week_ago).count()
    new_users_month = UserProfile.objects.filter(created_at__gte=month_ago).count()
    
    # Activity Statistics - Optimized with single query
    interactions_qs = MealInteraction.objects.exclude(chosen_food__isnull=True)
    total_interactions = interactions_qs.count()
    interactions_today = interactions_qs.filter(created_at__date=today).count()
    interactions_week = interactions_qs.filter(created_at__gte=week_ago).count()
    
    # Food Statistics
    total_foods = Food.objects.count()
    foods_by_meal = list(Food.objects.values('meal_type').annotate(count=Count('id')))
    
    # Most Popular Foods (Top 10) - Single query with annotation
    popular_foods = Food.objects.annotate(
        interaction_count=Count('chosen_in')
    ).filter(interaction_count__gt=0).order_by('-interaction_count')[:10]
    
    # User Demographics - Single queries each
    gender_distribution = list(UserProfile.objects.values('gender').annotate(count=Count('id')))
    goal_distribution = list(UserProfile.objects.values('goal').annotate(count=Count('id')))
    activity_distribution = list(UserProfile.objects.values('activity').annotate(count=Count('id')))
    diet_distribution = list(UserProfile.objects.values('diet').annotate(count=Count('id')))
    
    # Average User Metrics
    avg_metrics = UserProfile.objects.aggregate(
        avg_age=Avg('age'),
        avg_bmi=Avg('bmi'),
        avg_calorie_goal=Avg('daily_calorie_goal')
    )
    avg_age = avg_metrics['avg_age'] or 0
    avg_bmi = avg_metrics['avg_bmi'] or 0
    avg_calorie_goal = avg_metrics['avg_calorie_goal'] or 0
    
    # Daily Activity for Last 30 Days - Optimized aggregation
    daily_activity_qs = (
        MealInteraction.objects
        .filter(created_at__gte=today - timedelta(days=29))
        .exclude(chosen_food__isnull=True)
        .values('created_at__date')
        .annotate(count=Count('id'))
        .order_by('created_at__date')
    )
    
    # Convert to dict for quick lookup
    activity_dict = {entry['created_at__date']: entry['count'] for entry in daily_activity_qs}
    
    # Fill in missing days
    daily_activity = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        daily_activity.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': activity_dict.get(date, 0)
        })
    
    # User Growth Over Time (Last 30 Days) - More efficient
    user_growth_qs = (
        UserProfile.objects
        .filter(created_at__date__lte=today, created_at__date__gte=today - timedelta(days=29))
        .values('created_at__date')
        .annotate(count=Count('id'))
        .order_by('created_at__date')
    )
    
    # Cumulative count
    base_count = UserProfile.objects.filter(created_at__date__lt=today - timedelta(days=29)).count()
    cumulative = base_count
    growth_dict = {}
    
    for entry in user_growth_qs:
        cumulative += entry['count']
        growth_dict[entry['created_at__date']] = cumulative
    
    user_growth = []
    for i in range(30):
        date = today - timedelta(days=29-i)
        if date in growth_dict:
            cumulative = growth_dict[date]
        user_growth.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': cumulative
        })
    
    context = {
        'total_users': total_users,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'total_interactions': total_interactions,
        'interactions_today': interactions_today,
        'interactions_week': interactions_week,
        'total_foods': total_foods,
        'foods_by_meal': foods_by_meal,
        'popular_foods': popular_foods,
        'gender_distribution': gender_distribution,
        'goal_distribution': goal_distribution,
        'activity_distribution': activity_distribution,
        'diet_distribution': diet_distribution,
        'avg_age': round(avg_age, 1),
        'avg_bmi': round(avg_bmi, 1),
        'avg_calorie_goal': round(avg_calorie_goal, 0),
        'daily_activity': daily_activity,
        'user_growth': user_growth,
    }
    
    return render(request, 'dashboard/home.html', context)


@staff_member_required
def users_list(request):
    """User management page with detailed list"""
    from django.db.models import Count
    
    # Optimized query with aggregation
    users = UserProfile.objects.select_related('user').annotate(
        interaction_count=Count('meal_interactions', filter=Q(meal_interactions__chosen_food__isnull=False))
    ).order_by('-created_at')
    
    context = {
        'users': users,
    }
    return render(request, 'dashboard/users_list.html', context)


@staff_member_required
def user_detail(request, user_id):
    """Detailed view of a single user"""
    profile = UserProfile.objects.select_related('user').get(id=user_id)
    
    # User's meal history - DON'T slice yet, we need to filter first
    interactions_base = MealInteraction.objects.filter(
        user=profile
    ).select_related('chosen_food').exclude(
        chosen_food__isnull=True
    ).order_by('-created_at')
    
    # User's statistics
    total_calories = interactions_base.aggregate(
        total=Sum('chosen_food__calories_kcal')
    )['total'] or 0
    
    meal_type_breakdown = interactions_base.values('meal_type').annotate(
        count=Count('id')
    )
    
    # Last 7 days activity
    week_ago = timezone.now() - timedelta(days=7)
    
    # Now we can safely slice for display
    interactions = interactions_base[:50]
    
    daily_calories = []
    for i in range(7):
        date = timezone.now().date() - timedelta(days=6-i)
        day_cals = MealInteraction.objects.filter(
            user=profile,
            created_at__date=date
        ).exclude(chosen_food__isnull=True).aggregate(
            total=Sum('chosen_food__calories_kcal')
        )['total'] or 0
        daily_calories.append({
            'date': date.strftime('%Y-%m-%d'),
            'calories': round(day_cals, 0)
        })
    
    context = {
        'profile': profile,
        'interactions': interactions,
        'total_calories': round(total_calories, 0),
        'meal_type_breakdown': list(meal_type_breakdown),
        'daily_calories': daily_calories,
    }
    return render(request, 'dashboard/user_detail.html', context)


@staff_member_required
def foods_list(request):
    """Food management page"""
    foods = Food.objects.all().order_by('meal_type', 'name')
    
    # Add popularity count
    for food in foods:
        food.usage_count = MealInteraction.objects.filter(
            chosen_food=food
        ).count()
    
    # Calculate meal type counts
    breakfast_count = Food.objects.filter(meal_type='breakfast').count()
    lunch_count = Food.objects.filter(meal_type='lunch').count()
    dinner_count = Food.objects.filter(meal_type='dinner').count()
    snack_count = Food.objects.filter(meal_type='snack').count()
    
    context = {
        'foods': foods,
        'breakfast_count': breakfast_count,
        'lunch_count': lunch_count,
        'dinner_count': dinner_count,
        'snack_count': snack_count,
    }
    return render(request, 'dashboard/foods_list.html', context)


@staff_member_required
def analytics(request):
    """Advanced analytics page"""
    
    # Time-based meal patterns
    meal_patterns = MealInteraction.objects.exclude(
        chosen_food__isnull=True
    ).values('meal_type').annotate(
        count=Count('id'),
        avg_calories=Avg('chosen_food__calories_kcal')
    )
    
    # Goal vs Activity distribution
    goal_activity_matrix = UserProfile.objects.values(
        'goal', 'activity'
    ).annotate(count=Count('id'))
    
    # Body type distribution
    body_type_dist = UserProfile.objects.values('body_type').annotate(
        count=Count('id'),
        avg_bmi=Avg('bmi'),
        avg_calorie_goal=Avg('daily_calorie_goal')
    )
    
    # Top performers (users closest to their goals)
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    user_performance = []
    for profile in UserProfile.objects.all()[:20]:
        week_calories = MealInteraction.objects.filter(
            user=profile,
            created_at__gte=week_ago
        ).exclude(chosen_food__isnull=True).aggregate(
            total=Sum('chosen_food__calories_kcal')
        )['total'] or 0
        
        goal_calories = (profile.daily_calorie_goal or 2000) * 7
        if goal_calories > 0:
            adherence = (week_calories / goal_calories) * 100
            user_performance.append({
                'username': profile.user.username,
                'adherence': round(adherence, 1),
                'week_calories': round(week_calories, 0),
                'goal_calories': round(goal_calories, 0)
            })
    
    user_performance.sort(key=lambda x: abs(100 - x['adherence']))
    
    context = {
        'meal_patterns': list(meal_patterns),
        'goal_activity_matrix': list(goal_activity_matrix),
        'body_type_dist': list(body_type_dist),
        'user_performance': user_performance[:10],
    }
    return render(request, 'dashboard/analytics.html', context)