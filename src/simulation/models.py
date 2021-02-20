from django.db import models
from django.urls import reverse
# Create your models here.
class Simulation(models.Model):
    ISIN                = models.CharField(max_length=50)
    strategie           = models.CharField(max_length=255, blank=True,default="default_wert") # Die ausgewählte Strategie
    von_datum           = models.DateField()
    bis_datum           = models.DateField()
    startkapital        = models.DecimalField(max_digits=30,decimal_places=2)
    nutzername          = models.CharField(max_length=30)
    

    def get_absolute_url(self):
        return reverse("simulation:simulation-ergebnis", kwargs={})