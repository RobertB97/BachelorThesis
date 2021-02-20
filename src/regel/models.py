from django.db import models
from django.urls import reverse




class Regel(models.Model):
    name                = models.CharField(max_length=50)
    beschreibung        = models.TextField()
    code                = models.TextField()
    nutzername          = models.CharField(max_length=30)

    def get_absolute_url(self):
        return reverse("regel:regel-details", kwargs={"id": self.id})
    