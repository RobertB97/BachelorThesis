from django.urls import path
from indikator.views import (
    IndikatorErstellenView,
    IndikatorListeView,
    IndikatorDetailView,
    IndikatorBearbeitenView,
    IndikatorEntfernenView,
)


app_name = 'indikator'
urlpatterns = [
    path('', IndikatorListeView.as_view(), name='indikator-liste'),
    path('erstellen/', IndikatorErstellenView.as_view(), name='indikator-erstellen'),
    path('<int:id>/', IndikatorDetailView.as_view(), name='indikator-details'),
    path('<int:id>/bearbeiten/', IndikatorBearbeitenView.as_view(), name='indikator-bearbeiten'),
    path('<int:id>/entfernen/', IndikatorEntfernenView.as_view(), name='indikator-entfernen'),
]
