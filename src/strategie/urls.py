
from django.urls import path
from .views      import (
    StrategieListeView,
    StrategieHinzufuegenView,
    StrategieFehlerView,
    StrategieDetailView,
    StrategieBearbeitenView,
    StrategieEntfernenView,
)
 
#URL Dispatch für Strategie-App

app_name    = 'strategie'
urlpatterns = [
    path('',                     StrategieListeView.as_view(),       name = 'strategie-liste'),
    path('hinzufuegen/',         StrategieHinzufuegenView.as_view(), name = 'strategie-hinzufuegen'),
    path('fehler/',              StrategieFehlerView.as_view(),      name = 'strategie-fehler'),
    path('<int:id>/',            StrategieDetailView.as_view(),      name = 'strategie-details'),
    path('<int:id>/bearbeiten/', StrategieBearbeitenView.as_view(),  name = 'strategie-bearbeiten'),
    path('<int:id>/entfernen/',  StrategieEntfernenView.as_view(),   name = 'strategie-entfernen'),
]