from django.urls     import path
from indikator.views import (
    IndikatorListeView,
    IndikatorHinzufuegenView,
    IndikatorFehlerView,
    IndikatorDetailView,
    IndikatorGraphView,
    IndikatorBearbeitenView,
    IndikatorEntfernenView,
    )

#URL Dispatch für Indikator-App

app_name    = 'indikator'
urlpatterns = [
    path('',                     IndikatorListeView.as_view(),       name = 'indikator-liste'),
    path('hinzufuegen/',         IndikatorHinzufuegenView.as_view(), name = 'indikator-hinzufuegen'),
    path('fehler/',              IndikatorFehlerView.as_view(),      name = 'indikator-fehler'),
    path('<int:id>/',            IndikatorDetailView.as_view(),      name = 'indikator-details'),
    path('<int:id>/graph/',      IndikatorGraphView.as_view(),       name = 'indikator-graph'),
    path('<int:id>/bearbeiten/', IndikatorBearbeitenView.as_view(),  name = 'indikator-bearbeiten'),
    path('<int:id>/entfernen/',  IndikatorEntfernenView.as_view(),   name = 'indikator-entfernen'),
]
