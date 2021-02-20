from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from .models import Simulation

from datetime import date


class SimulationModelForm(ModelForm):

    class Meta:
        model = Simulation
        fields = ["ISIN","strategie","von_datum","bis_datum",'startkapital']
        widgets = {
            "von_datum" : forms.DateInput(attrs={"type": "date"}),
            "bis_datum" : forms.DateInput(attrs={"type": "date"}),
            "strategie" : forms.HiddenInput(),
        }
        labels = {
            "von_datum": "Start-Datum",
            "bis_datum": "End-Datum"
        }
        

    def clean(self):
        #super(SimulationModelForm,self).clean()
        print(self.cleaned_data)
        von_datum = self.cleaned_data.get("von_datum")
        bis_datum = self.cleaned_data.get("bis_datum")
        datum_heute = date.today()
        
        if(von_datum > bis_datum):
            print("hey")
            raise ValidationError("von_datum sollte kleiner als bis_datum sein")
        if(von_datum > datum_heute or bis_datum > datum_heute):
            raise ValidationError("Daten für diesen Zeitintervall gibt es noch nicht")
        
        
        # if either date bigger than current date, throw error (data not yet available)
        # if von_datum > bis_datum say von_datum must be < bis_datum
        # basically if either date is out of the simulation range, just simulate as close the set boundaries, as possible
        