from django.db   import models
from django.urls import reverse
from django.core.validators import MaxLengthValidator

class Regel(models.Model):
    '''
    Klasse des Regel Models.
    Besteht aus den Felder "name", "beschreibung" und "berechnung_pseudo_code" 
    '''
    name                             = models.CharField(max_length = 100) # name darf max. 100 Zeichen haben
    beschreibung                     = models.TextField(validators=[MaxLengthValidator(1000)]) # beschreibung darf max. 100 Zeichen haben
    berechnung_pseudo_code           = models.TextField(validators=[MaxLengthValidator(2000)]) # berechnung_pseudo_code darf max. 100 Zeichen haben

    def get_absolute_url(self):
        """
        Jede Regel verweist auf die eigene Detail-Ansicht.
        """
        return reverse("regel:regel-details", kwargs = {"id" : self.id})
    