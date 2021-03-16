from django.contrib.auth import authenticate, get_user_model, login, logout
from django.forms.models import model_to_dict
from django.shortcuts    import redirect, render

from account.forms import (
    AccountAuthenticationForm,
    AccountUpdateForm,
    RegistrationForm
)


def registration_view(request):
    """
        Funktion der Registrierungs Ansicht.
        Hierbei wird nichts angezeigt, sondern nur die logout-Funktion ausgeführt und zur Login-Seite weitergeleitet
        Wenn HTTP Methode gleich GET:
            Leeres Registrierungs Formular anzeigen.
        Wenn HTTP Methode gleich POST:
            Wenn Daten valide sind, Nutzer authentifizieren, einloggen und auf den Home-Screen weiterleiten.
        """
    context = {}
    if request.POST:

        form = RegistrationForm(request.POST)

        if form.is_valid():
            form.cleaned_data["email"] = form.cleaned_data.get('email').lower()
            form.save()
            login(
                request = request,
                account = authenticate(
                    email    = form.cleaned_data.get('email'),
                    password = form.cleaned_data.get('password1')
                )
            )
            return redirect('/home/')
        else:
            context['registration_form'] = form
    else:  # GET request
        form = RegistrationForm()
        context['registration_form'] = form
    return render(request, 'account/register.html', {"form" : form})

def logout_view(request):
    """
        Funktion der Logout Ansicht.
        Hierbei wird nichts angezeigt, sondern nur die logout-Funktion ausgeführt und zur Login-Seite weitergeleitet.
        """
    logout(request)
    return redirect('/login/')

def login_view(request):
    """
        Funktion des Login-View. 

            Wenn HTTP Methode gleich GET
                Leeres Login Formular anzeigen
            Wenn HTTP Methode gleich POST
                Mit den Benutzerdaten wird eine Authentifizierung gemacht. 
                Wenn valid zum Home-Screen weiterleiten
        """

    if request.user.is_authenticated:
        return redirect("/home/")

    if request.POST:
        form = AccountAuthenticationForm(request.POST)

        if form.is_valid():
            request.user = authenticate(
                email    = request.POST['email'].lower(), 
                password = request.POST['password']
            )

            if request.user:
                login(request, request.user)
                return redirect("/home/")

    else:
        return render(request, 'account/login.html', {"form" : AccountAuthenticationForm()})

def account_view(request):
    """
        Funktion der Account Ansicht.
        Als erstes wird geprüft, ob der Nutzer authentifiziert ist. Wenn nicht, zum Login-Screen weiterleiten

        Wenn HTTP Methode gleich Get
            alle Nutzerdaten zum Template weitergeben
        Wenn HTTP Methode gleich POST
            Daten speichern wenn valid
        """

    if not request.user.is_authenticated:
        return redirect("/login/'")

    User        = get_user_model()
    users       = User.objects.get(email = request.user.email)
    datenDict   = model_to_dict(users)
    nutzerdaten = {
        'email'         : users.email.lower(),
        'username'      : users.username,
        'last_login'    : users.last_login,
        'date_joined'   : users.date_joined,
        'is_admin'      : datenDict['is_admin'],
        'is_staff'      : datenDict['is_staff'],
        'is_superuser:' : datenDict['is_superuser'],
    }
    return render(request, 'account/account.html', {"daten" : nutzerdaten})

def account_edit_view(request):
    """
        Funktion der Account Ansicht.
        Als erstes wird geprüft, ob der Nutzer authentifiziert ist. Wenn nicht, zum Login-Screen weiterleiten

        Wenn HTTP Methode gleich POST
            wenn Eingabedaten valid sind
            alle Buchstaben der email in Kleinbuchstaben umwandel
            veränderten NutzerDaten speichern 
            weiterleiten zur Profilansicht
            
        Wenn HTTP Methode gleich GET
            Formular mir der aktuell verwendeten Email-Adresse rendern
            
        """

    if not request.user.is_authenticated:
        return redirect("/login/")

    if request.POST:
        form = AccountUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.cleaned_data["email"] = form.cleaned_data["email"].lower()
            form.save()
            return redirect("/profil/")
    else:
        form = AccountUpdateForm(
            initial = {"email" : request.user.email.lower()}
        )
    return render(request, 'account/edit_account.html', {"form" : form})
