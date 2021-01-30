from django import forms
from .models import Indikator



class IndikatorModelForm(forms.ModelForm):
    class Meta:
        model = Indikator
        fields = ('name','beschreibung','code')        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'john'}),
            'beschreibung': forms.Textarea(attrs={'class':'form-control'}),
            'code': forms.Textarea(attrs={'class':'johnny'}),
        }

    
   
