from account.views import (
    registration_view,
    logout_view,
    login_view,
    account_view,
    account_edit_view,
)

from django.conf.urls.static import static
from django.contrib          import admin
from django.urls             import include, path
from django.views.generic    import TemplateView


#allgemeiner URL Dispatch für TechTrader

urlpatterns = [
    #Adminseite, Zugang nur mit superuser
    path('admin/', admin.site.urls),

    #Allgemein zugängliche Seiten
    path('',       TemplateView.as_view(template_name = "home.html"),  name = "home-view"),
    path('home/',  TemplateView.as_view(template_name = "home.html"),  name = "home-view"),
    path('about/', TemplateView.as_view(template_name = "about.html"), name = "about"),
    

    # Seiten für User Management
    path('registrieren/',      registration_view, name = "registrierung-view"),
    path('logout/',            logout_view,       name = "logout-view"),
    path('login/',             login_view,        name = "login-view"),
    path('profil/',            account_view,      name = "profil-view"),
    path('profil/bearbeiten/', account_edit_view, name = "bearbeiten-view"),

    #TechTrader Apps
    path('simulationen/', include('simulation.urls'), name = "simulationen-app"),
    path('strategien/',   include('strategie.urls'),  name = "strategien-app"),
    path('regeln/',       include('regel.urls'),      name = "regeln-app"),
    path('indikatoren/',  include('indikator.urls'),  name = "indikatoren-app"),
]
