from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account

# Das Form für die Registrierung eines neuen Nutzers, die Felder email, password1 und password2 werden von UserCreationForm geerbt
# Deren angezeigte labels werden in der __init__ funktion überschrieben und die hilftexte werden auf None gesetzt
class RegistrationForm(UserCreationForm):
	email = forms.EmailField(max_length=60)

	class Meta:
		model = Account
		# password1 und password2 werden auf Gleichheit von UserCreationForm geprüft
		fields = ("email", "username", "password1", "password2")
		labels = {
			'username': 'Nutzername'
        }

	def __init__(self, *args, **kwargs):
		super(RegistrationForm, self).__init__(*args, **kwargs)

		for fieldname in ['username', 'password1', 'password2']:
			self.fields[fieldname].help_text = None

		self.fields['email'].label = 'E-Mail'
		self.fields['password1'].label = 'Passwort'
		self.fields['password2'].label = 'Passwort bestätigen'
		
# Für das Einlogen wird die email und das passwort benötigt, 
class AccountAuthenticationForm(forms.ModelForm):

	password = forms.CharField(label='Password', widget=forms.PasswordInput)

	class Meta:
		model = Account
		fields = ('email', 'password')

	def __init__(self, *args, **kwargs):
		super(AccountAuthenticationForm, self).__init__(*args, **kwargs)

		self.fields['email'].label = 'E-Mail'
		self.fields['password'].label = 'Passwort'

	

	def clean(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			password = self.cleaned_data['password']
			if not authenticate(email=email, password=password):
				raise forms.ValidationError("Invalid login")


# Beim Bearbeiten eines Accountprofils können die E-Mail und der Nutzername geändert werden, dabei wird geprüft ob diese einzigartig sind
class AccountUpdateForm(forms.ModelForm):

	class Meta:
		model = Account
		fields = ('email',)

	def clean_email(self):
		if self.is_valid():
			email = self.cleaned_data['email']
			try:
				account = Account.objects.exclude(pk=self.instance.pk).get(email=email)
			except Account.DoesNotExist:
				return email
			raise forms.ValidationError('Email "%s" wird bereits verwendet.' % email)
