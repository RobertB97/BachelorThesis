from django.db import models
from django.urls import reverse

# Create your models here. 
class Simulation(models.Model):
    '''
    Klasse des Simulation Models.
    Besteht aus den Felder "isin", "strategie", "von_datum", "bis_datum", und "startkapital"
    '''
    isin                = models.CharField(max_length=12,blank=True,null=True)  # Die ausgewählte ISIN
    strategie           = models.CharField(max_length=255,blank=True,null=True) # Die ausgewählte Strategie
    von_datum           = models.DateField()
    bis_datum           = models.DateField()
    startkapital        = models.IntegerField()
    

    def get_absolute_url(self):
        """
        Wird als "Success-url" bei erfolgreichem Ausfüllen des Forms verwendet.
        """
        return reverse("simulation:simulation-ergebnis", kwargs={})
