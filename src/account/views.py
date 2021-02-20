from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from account.forms import RegistrationForm, AccountAuthenticationForm, AccountUpdateForm
from django.contrib.auth import get_user_model
from django.forms.models import model_to_dict

def registration_view(request):
	context = {}
	if request.POST:
		form = RegistrationForm(request.POST)
		if form.is_valid():
			form.save()
			email = form.cleaned_data.get('email')
			raw_password = form.cleaned_data.get('password1')
			account = authenticate(email=email, password=raw_password)
			login(request, account)
			return redirect('/home/')
		else:
			context['registration_form'] = form
	else: #GET request
		form = RegistrationForm()
		context['registration_form'] = form
	return render(request, 'account/register.html', {"form":form})



def logout_view(request):
	logout(request)
	return redirect('/login/')



def login_view(request):

	context = {}

	user = request.user
	if user.is_authenticated:
		return redirect("/home/")

	if request.POST:
		form = AccountAuthenticationForm(request.POST)

		 
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user = authenticate(email=email, password=password)

			if user:
				login(request, user)
				return redirect("/home/")

	else:
		form = AccountAuthenticationForm()

	return render(request, 'account/login.html', {"form":form})



def account_view(request):

	if not request.user.is_authenticated:
		return redirect("/login/'")

	context = {}

	if request.POST:
		form = AccountUpdateForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
	else:
		User = get_user_model()
		users = User.objects.get(email=request.user.email)
		datenDict = model_to_dict(users)
		nutzerdaten = {
			'email': users.email, 
			'username':users.username,
			'last_login': users.last_login,
			'date_joined': users.date_joined,
			'is_admin': datenDict['is_admin'],
			'is_staff': datenDict['is_staff'],
			'is_superuser': datenDict['is_superuser'],
		}
	return render(request, 'account/account.html', {"daten":nutzerdaten})

def account_edit_view(request):

	if not request.user.is_authenticated:
		return redirect("/login/")


	if request.POST:
		form = AccountUpdateForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			return redirect("/profil/")
	else:
		form = AccountUpdateForm(
				initial= {
					"email": request.user.email,
					"username": request.user.username,

				}
			)
	return render(request, 'account/edit_account.html', {"form":form})


	