from django.db import models
from django.urls import reverse
from regel.models import Regel
from jsonfield import JSONField

# Create your models here.
class Strategie(models.Model):
    name = models.CharField(max_length=50)
    beschreibung = models.TextField()
    regeln = models.CharField(max_length=10000)
    # CHOICES =  {}
    # ALLOBJECTS = Regel.objects.all()
    # for i in ALLOBJECTS:
    #     CHOICES.append(model_to_dict(ALLOBJECTS[i].get))

    # regel = models.CharField(max_length=100, choices=CHOICES)

    def get_absolute_url(self):
        return reverse("strategie:strategie-details", kwargs={"id": self.id})
    
    