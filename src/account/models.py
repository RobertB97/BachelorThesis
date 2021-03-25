from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class MyAccountManager(BaseUserManager):
	"""
		Klasse für das Erstellen von Nutzer-Accounts und Supernutzer-Accounts.

		Methoden
        --------
        create_user 
            Funktion für das Erstellen von neuen Nutzer-Accounts

		create_superuser 
            Funktion für das Erstellen von neuen Supernutzer-Accounts
		"""

	def create_user(self, email, username, password = None):
		"""
			Funktion für das Erstellen von neuen Nutzer-Accounts

			Wenn keine E-Mail oder kein Nutzername angegeben wurde, wird entsprechende Fehlermeldung geworfen.
			Ansonsten neues Account-Objekt erstellen mit dem die gesamten Nutzerdaten in der DB gespeichert werden.

			"""

		if not email:
			raise ValueError("Für die Erstellung eines Accounts wird eine E-Mail Adresse benötigt")
		if not username:
			raise ValueError("Für die Erstellung eines Accounts wird ein Nutzername benötigt")

		user  = self.model(
				email 	 = self.normalize_email(email),
				username = username,
			)

		user.set_password(password)
		user.save(using = self._db)
		return user

	def create_superuser(self, email, username, password):
		"""
			Funktion für das Erstellen von neuen Supernutzer-Accounts (aktuell nur zugänglich in Konsole)

			Wenn keine E-Mail oder kein Nutzername angegeben wurde, wird entsprechende Fehlermeldung geworfen.
			Ansonsten neues Supernutzer-Account-Objekt erstellen mit dem die gesamten Nutzerdaten in der DB gespeichert werden.

			"""

		if not email:
			raise ValueError("Für die Erstellung eines Accounts wird eine E-Mail Adresse benötigt")
		if not username:
			raise ValueError("Für die Erstellung eines Accounts wird ein Nutzername benötigt")

		user = self.create_user(
				email    = self.normalize_email(email),
				password = password,
				username = username,
			)
		user.is_admin 	  = True
		user.is_staff	  = True
		user.is_superuser = True
		user.save(using=self._db)
		return user


class Account(AbstractBaseUser):
	"""	
		Klasse der Account-Objekte.
		Hier werden alle Account Eigenschaften festgelegt .

		"""
	email 		 = models.EmailField(verbose_name = "email", max_length = 60, unique = True)
	username 	 = models.CharField(max_length = 30, unique = True)
	date_joined	 = models.DateTimeField(verbose_name = 'date joined', auto_now_add = True)
	last_login	 = models.DateTimeField(verbose_name = 'last login', auto_now = True)
	is_admin	 = models.BooleanField(default = False)
	#is_active	 = models.BooleanField(default = True)
	is_staff	 = models.BooleanField(default = False)
	is_superuser = models.BooleanField(default = False)

	USERNAME_FIELD  = 'email'
	REQUIRED_FIELDS = ['username', ]

	objects = MyAccountManager()

	def __str__(self):
		return self.email

	def has_perm(self, perm, obj=None):
		return self.is_admin

	def has_module_perms(self, app_label):
		return True
