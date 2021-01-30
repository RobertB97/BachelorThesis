from django.db import models
from django.urls import reverse




class Regel(models.Model):
    name = models.CharField(max_length=50)
    beschreibung = models.TextField()
    code = models.TextField()

    def get_absolute_url(self):
        return reverse("regel:regel-detail", kwargs={"id": self.id})
    


    """
    name = models.CharField(max_length=50)
    ACTION_CHOICES = [("B", "Buy"), ("S", "Sell"), ("H", "Hold")]
    action = models.CharField(
        max_length=4, 
        choices=ACTION_CHOICES, 
        default="H"
    )
    COMPARISON_CHOICES = [(">", ">"), ("<", "<"), ("=", "="), ("<=", "<="), (">=", ">=")]
    comparison_type = models.CharField(
        max_length=2, 
        choices=COMPARISON_CHOICES, 
        default=">"
    )
    multiply_factor = models.DecimalField(max_digits=10, decimal_places=2, default=1) # if for example a multiple of the current share prices is needed
    
    COMPARE_PARTNER_ONE_CHOICES = [("Stock", "Stock"), ("Indicator","Indicator")]
    compare_partner_one_type = models.CharField(
        max_length=9, 
        choices=COMPARE_PARTNER_ONE_CHOICES, 
        default="Stock"
    )
    compare_partner_one = models.IntegerField() #  refers to the id of either the chosen stock or indicator
    
    COMPARE_PARTNER_TWO_CHOICES = [("Stock", "Stock"), ("Indicator","Indicator"),("Number", "Number")]
    compare_partner_two_type = models.CharField(
        max_length=9, 
        choices=COMPARE_PARTNER_TWO_CHOICES, 
        default="Stock"
    )
    compare_partner_two = models.IntegerField() # refers to the id of either the chosen stock or indicator for compare partner two
    compare_partner_two_as_number = models.DecimalField(max_digits= 20, decimal_places=4) # used when comparing to a number instead stock/indicator

    transaction_amount = models.CharField(
        max_length=20,
        default=1
    )
    """