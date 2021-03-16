from django.db   import models
from django.urls import reverse

from django.core.validators import MaxLengthValidator 

class Indikator(models.Model):
  '''
    Klasse des Indikator Models.
    Besteht aus den Felder "name", "beschreibung", "berechnung_pseudo_code" und "eigene_skala"
  '''
  name                      = models.CharField(max_length = 100) # name darf max. 100 Zeichen haben
  beschreibung              = models.TextField(validators=[MaxLengthValidator(1000)]) # beschreibung darf max. 100 Zeichen haben
  berechnung_pseudo_code    = models.TextField(validators=[MaxLengthValidator(2000)]) # berechnung_pseudo_code darf max. 100 Zeichen haben
  eigene_skala              = models.BooleanField() 
  
  def get_absolute_url(self):
    """
      Jeder Indikator verweist auf die eigene Detail-Ansicht.
      """
    return reverse("indikator:indikator-details", kwargs = {"id" : self.id})
    
    