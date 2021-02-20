from django.db import models
from django.urls import reverse
from regel.models import Regel

# Alle Felder von einem Strategie Objekt
class Strategie(models.Model):
    name                = models.CharField(max_length=50)
    beschreibung        = models.TextField()
    regeln              = models.CharField(max_length=100) # Hier wird eine Liste von RegelIDs gespeichert
    nutzername          = models.CharField(max_length=30)

    def get_absolute_url(self):
        return reverse("strategie:strategie-details", kwargs={"id": self.id})
    
    