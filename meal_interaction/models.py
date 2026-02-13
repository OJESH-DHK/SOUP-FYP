from django.db import models
from user.models import UserProfile
from food_api.models import Food
from core.models import CommonModel
# Create your models here.
class MealInteraction(CommonModel):
    MEAL_CHOICES = [
        ("breakfast", "Breakfast"),
        ("lunch", "Lunch"),
        ("dinner", "Dinner"),
        ("snack", "Snack"),
    ]

    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="meal_interactions"
    )

    day = models.IntegerField()
    meal_type = models.CharField(max_length=20, choices=MEAL_CHOICES)
    target_cal = models.FloatField()

    food_1 = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        null=True,
        related_name="shown_as_1"
    )
    food_2 = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        null=True,
        related_name="shown_as_2"
    )
    food_3 = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        null=True,
        related_name="shown_as_3"
    )

    chosen_food = models.ForeignKey(
        Food,
        on_delete=models.SET_NULL,
        null=True,
        related_name="chosen_in"
    )



    class Meta:
        pass

        #constraints = [
            #models.UniqueConstraint(
                #fields=["user", "day", "meal_type"],
                #name="unique_user_day_meal"
            #)
        #]
        #indexes = [
            #models.Index(fields=["user", "day"]),
            #models.Index(fields=["meal_type", "day"]),
        #]

    #def __str__(self):
        #return f"{self.user.user_id} day {self.day} {self.meal_type}"