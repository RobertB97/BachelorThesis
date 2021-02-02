from django.db import models
from django.urls import reverse
from regel.models import Regel

class Strategie(models.Model):
    name = models.CharField(max_length=50)
    beschreibung = models.TextField()
    regeln = models.CharField(max_length=100)


    def get_absolute_url(self):
        return reverse("strategie:strategie-details", kwargs={"id": self.id})
    
    