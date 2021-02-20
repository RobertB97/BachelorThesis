from django import forms
from .models import Indikator



class IndikatorModelForm(forms.ModelForm):
    class Meta:
        model = Indikator
        fields = ('name','beschreibung','code')        
        widgets = {
            'name': forms.TextInput(attrs={'class': 'inputname'}),
            'beschreibung': forms.Textarea(attrs={'class':'beschreibung','cols':"50",'rows':"4"}),
            # 'code': forms.Textarea(attrs={'class':'code'}),
            'code': forms.Textarea(attrs={}),
            
        }


    
   
