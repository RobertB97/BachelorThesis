from django.db import models
from django.urls import reverse
# Create your models here.
class Simulation(models.Model):
    name = models.CharField(max_length=50)
    strategie = models.CharField(max_length=255, blank=True,default="test")
    von_datum = models.DateField()
    bis_datum = models.DateField()


    def get_absolute_url(self):
        return reverse("simulation:simulation-ergebnis", kwargs={})