from django.db import models
from django.urls import reverse



class Indikator(models.Model):
  name = models.CharField(max_length=50)
  beschreibung = models.TextField()
  code = models.TextField()

  def get_absolute_url(self):
    return reverse("indikator:indikator-details", kwargs={"id": self.id})
    
    