from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate

from account.models import Account

class RegistrationForm(UserCreationForm):
	"""
		Klasse des Registrierungs Formulars. 
		Hier werden die angezeigten Formularfelder, deren CSS Klassen und ihr Aussehen definiert.
		Um einen Account zu erstellen, müssen ein einzigartiger Nutzernamen, 
		eine einzigartige Email und ein Passwort angegeben werden.
		"""
	email = forms.EmailField(max_length = 60, error_messages = {"invalid" : "Ungültige Email."})

	error_messages = {
        	'password_mismatch': ("Die Passwörter waren nicht gleich."),
    	}
	class Meta:
		model  = Account
		fields = (
			"username", 
			"email", 
			"password1", 
			"password2"
		)
		labels = { # Liste aller Felder die von dem Model Indikator verwendet werden
			'username' : 'Nutzername'
        }
		widgets = { # hier werden die Felderarten und css Klassen festgelegt.
			'username'  : forms.TextInput(attrs = {'class' : 'logintags'}),
			'email'     : forms.TextInput(attrs = {'class' : 'logintags'}),
			'password1' : forms.PasswordInput(attrs = {'class' : 'logintags'}),
			'password2' : forms.PasswordInput(attrs = {'class' : 'logintags'}),
		}
		

	def __init__(self, *args, **kwargs):
		"""
			Wird nur verwendet um die Labels der Felder zu ändern. 
			Bei den Account Feldern geht das Ändern der Labels nur auf diese Art und Weise.
			"""
		super(RegistrationForm, self).__init__(*args, **kwargs)

		for fieldname in ['username', 'password1', 'password2']:
			self.fields[fieldname].help_text = None

		self.fields['email'].label 	   = 'E-Mail'
		self.fields['password1'].label = 'Passwort'
		self.fields['password2'].label = 'Passwort bestätigen'
	
	def clean_email(self):
		"""
			Hier wird geprüft ob die Email einzigartig ist und in keinem anderen Account verwendet wird.
			Wenn Account mit der angegebenen Email gefunden, Fehler werfen.
		"""
		email = self.cleaned_data['email'].lower()
		
		try:
			match = Account.objects.get(email = email) # Versuche Account Objekt mit angegebenen Email zu holen
		except Account.DoesNotExist:
			# Wenn kein Account mit der angegebenen Email gefunden wurde, dann Email weitergeben
			return email
		# ansonsten Fehlermeldung werfen
		raise forms.ValidationError("Email wird bereits verwendet.")

	def clean_username(self):
		"""
			Hier wird geprüft ob der Nutzername einzigartig ist und in keinem anderen Account verwendet wird.
			Wenn Account mit der angegebenen Email gefunden, Fehler werfen.
			"""
		username = self.cleaned_data['username'].lower()
		try:
			match = Account.objects.get(username = username) # Versuche Account Objekt mit angegebenen Nutzernamen zu holen
		except Account.DoesNotExist:
			# Wenn kein Account mit dem angegebenen Nutzernamen gefunden wurde, dann Nutzername weitergeben
			return username
		# ansonsten Fehlermeldung werfen
		raise forms.ValidationError("Nutzername wird bereits verwendet.")
		
class AccountAuthenticationForm(forms.ModelForm):
	"""
		Klasse des Anmelde Formulars. 
		Hier werden die angezeigten Formularfelder, deren CSS Klassen und ihr Aussehen definiert.
		Für das Einlogen wird die Email und das Passwort benötigt.
		"""
	email  = forms.EmailField(
		widget = forms.EmailInput(attrs = {
			'autocomplete' : 'off',
			'class'		   : 'form-control',
			'required'	   : 'required'
			}
		),
		error_messages={'invalid' : 'Ungültige E-Mail Adresse'}
	)

	class Meta:
		model   = Account
		fields  = ('email', 'password')
		widgets = {

			'password' : forms.PasswordInput(attrs = {'class': 'logintags'}),
		}

	def __init__(self, *args, **kwargs):
		"""
			Wird nur verwendet um die Labels der Felder zu ändern.
			Bei den Account Feldern geht das Ändern der Labels nur auf diese Art und Weise.
			"""
		super(AccountAuthenticationForm, self).__init__(*args, **kwargs)

		self.fields['email'].label    = 'E-Mail'
		self.fields['password'].label = 'Passwort'

	def clean(self):
		"""
			Hier wird geprüft ob die eingegebenen Nutzerdaten gültig sind.
			Wenn nein, dann wird ein Fehler geworfen.
			Wenn ja, dann ist der Nutzer authentifiziert.
			"""

		if self.is_valid():
			email    = self.cleaned_data['email'].lower()
			password = self.cleaned_data['password']
			if not authenticate(email = email, password = password):
				raise forms.ValidationError("Ungültige Benutzerdaten")

class AccountUpdateForm(forms.ModelForm):
	"""
		Klasse des Account Bearbeitungs Formulars . 
		Hier werden die angezeigten Formularfelder, deren CSS Klassen und ihr Aussehen definiert.
		Beim Bearbeiten eines Accountprofils kann nur die E-Mailgeändert werden, dabei wird geprüft ob diese einzigartig ist.
		Der Nutzername kann noch nicht geändert werden, 
		da die Änderungen auch im Backend getätigt werden müssten, was aber noch nicht geht.
		"""
	class Meta:
		model  = Account
		fields = ('email',)

	def clean_email(self):
		"""
			Hier wird geprüft ob die Email einzigartig ist und in keinem anderen Account verwendet wird.
			Wenn Account mit der angegebenen Email gefunden, Fehler werfen.
			"""
		if self.is_valid():
			email = self.cleaned_data['email']
			try:
				account = Account.objects.exclude(pk = self.instance.pk).get(email = email)
			except Account.DoesNotExist:
				return email
			raise forms.ValidationError('Email "%s" wird bereits verwendet.' % email)
