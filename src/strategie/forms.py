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
            'name': forms.TextInput(attrs={'class': 'inputname'}),
            'beschreibung': forms.Textarea(attrs={'class':'beschreibung','cols':"50",'rows':"4"}),
            'regeln': forms.HiddenInput
        }

    


   
