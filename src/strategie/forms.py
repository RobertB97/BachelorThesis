from django  import forms
from .models import Strategie

class StrategieModelForm(forms.ModelForm):
    """
        Klasse für das Definieren der Felder des Strategie Formulars.
        Ein StrategieFormular hat die Felder "name", "beschreibung" und "regeln".
        """
    class Meta:
        model = Strategie
        fields = [ #Liste aller Felder die von dem Model Strategie verwendet werden
            "name",
            "beschreibung",
            'regeln'
        ] 
        widgets = {  # hier werden die Felderarten und css Klassen festgelegt.
            'name'        : forms.TextInput(attrs={'class' : 'nameFeld'}),
            'beschreibung': forms.Textarea(attrs ={'class' : 'textfeld'}),
            'regeln'      : forms.HiddenInput # Dieses Feld wird vom System mit der getroffenen Wahl befüllt. Ist aber für Nutzer nicht sichtbar
        }
 


   
