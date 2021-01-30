from django import forms
from .models import Strategie
from regel.models import Regel
from django.forms.models import model_to_dict


class StrategieModelForm(forms.ModelForm):



    class Meta:

        model = Strategie
        fields = [
            "name",
            "beschreibung",
            'regeln'
      
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'beschreibung': forms.Textarea(attrs={'class':'form-control'}),
            'regeln': forms.HiddenInput
        }
    
    def clean(self):
        regelDaten = self.cleaned_data['regeln']
        regelDaten = regelDaten[1:-1]
        self.cleaned_data['regeln'] = regelDaten
        print(self.cleaned_data)

   
