from django       import forms
from django.forms import ModelForm

from datetime import date, datetime

from .models  import Simulation


class SimulationModelForm(ModelForm):
    """
        Klasse für das Definieren der Felder des Simulation Konfigurations Formulars.
        Ein Konfigurations Formular hat die Felder "isin", "von_datum", "bis_datum", "strategie" und "startkapital".
        """
    class Meta:
        model = Simulation
        fields = [ #Liste aller Felder die von dem Model Simulation verwendet werden
            "isin",  
            "strategie", 
            "von_datum", 
            "bis_datum", 
            "startkapital"
        ]
        widgets = { # hier werden die Felderarten und css Klassen festgelegt.
            "isin"         : forms.HiddenInput(), # Dieses Feld wird vom System mit der getroffenen Wahl befüllt. Ist aber für Nutzer nicht sichtbar
            "von_datum"    : forms.DateInput(attrs={"type" : "date"}),
            "bis_datum"    : forms.DateInput(attrs={"type" : "date"}),
            "strategie"    : forms.HiddenInput(), # Dieses Feld wird vom System mit der getroffenen Wahl befüllt. Ist aber für Nutzer nicht sichtbar
            "startkapital" : forms.NumberInput(attrs={"step" : "1","min" : "100"}) 
        }
        labels = { # hier werden die Labels angepasst
            "von_datum": "Start-Datum",
            "bis_datum": "End-Datum"
        }
        
