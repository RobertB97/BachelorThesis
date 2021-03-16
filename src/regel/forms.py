from django  import forms
from .models import Regel


class RegelModelForm(forms.ModelForm):
    """
        Klasse für das Definieren der Felder des Regel Formulars.
        Ein RegelFormular hat die Felder "name", "beschreibung" und "berechnung_pseudo_code".
        """
    class Meta:
        model   = Regel
        fields  = [ #Liste aller Felder die von dem Model Regel verwendet werden
            "name", 
            "beschreibung",
            "berechnung_pseudo_code",
        ]
        widgets = { # hier werden die Felderarten und css Klassen festgelegt.
            'name'                   : forms.TextInput(attrs = {'class' : 'nameFeld'}), 
            'beschreibung'           : forms.Textarea(attrs  = {'class' : 'textfeld'}),
            'berechnung_pseudo_code' : forms.Textarea(attrs  = {'class' : 'textfeld'}),
        }
        labels  = { # hier werden die Labels angepasst
			'berechnung_pseudo_code' : 'Code' # Das Label für das feld "berechnung_pseudo_code" soll "Code" sein
        }