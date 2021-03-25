from django  import forms
from .models import Indikator

class IndikatorModelForm(forms.ModelForm):
    """
        Klasse für das Definieren der Felder des Indikator Formulars.
        Ein IndikatorFormular hat die Felder "name", "beschreibung" und "berechnung_pseudo_code".
        """
    class Meta:
        model   = Indikator
        fields  = ( # Liste aller Felder die von dem Model Indikator verwendet werden
            'name',
            'beschreibung',
            'berechnung_pseudo_code',
            'eigene_skala'
        )        
        widgets =  { # hier werden die Felderarten und css Klassen festgelegt.
            'name'                  : forms.TextInput(attrs = {'class': 'nameFeld'}),
            'beschreibung'          : forms.Textarea(attrs  = {'class': 'textfeld'}),
            'berechnung_pseudo_code': forms.Textarea(attrs  = {'class': 'textfeld'}),
        }
        


     
   
