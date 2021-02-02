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
            'name': forms.TextInput(attrs={'class': 'inputname'}),
            'beschreibung': forms.Textarea(attrs={'class':'beschreibung','cols':"50",'rows':"4"}),
            'code': forms.Textarea(attrs={'class':'code'}),
        }

    def clean(self):
    #     cleanCode = self.cleaned_data['code']
    #     cleanCode = cleanCode.replace('\r\n',';')
    #     self.cleaned_data['code']=cleanCode
        print(self.cleaned_data)
