from django.db    import models
from django.urls  import reverse
from regel.models import Regel

from django.core.validators import MaxLengthValidator 
 
# Alle Felder von einem Strategie Objekt
class Strategie(models.Model):
    '''
    Klasse des Strategie Models.
    Besteht aus den Felder "name", "beschreibung" und "regeln" 
    '''
    name                = models.CharField(max_length = 100)
    beschreibung        = models.TextField(validators=[MaxLengthValidator(1000)])
    regeln              = models.CharField(max_length = 500) # Hier wird eine Liste von RegelIDs gespeichert

    def get_absolute_url(self):
        """
        Jede Strategie verweist auf die eigene Detail-Ansicht.
        """ 
        return reverse("strategie:strategie-details", kwargs = {"id" : self.id})
    
    