from django import forms
from .models import Regel


class RegelModelForm(forms.ModelForm):
    class Meta:
        model = Regel
        fields = [
            "name", 
            "beschreibung",
            "code",
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'beschreibung': forms.Textarea(attrs={'class':'form-control'}),
            'code': forms.Textarea(attrs={'class':'form-control'}),
        }

    def clean(self):
    #     cleanCode = self.cleaned_data['code']
    #     cleanCode = cleanCode.replace('\r\n',';')
    #     self.cleaned_data['code']=cleanCode
        print(self.cleaned_data)
