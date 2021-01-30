
from django.urls import path
from .views import (
    StrategieErstellenView,
    StrategieListeView,
    StrategieDetailView,
    StrategieBearbeitenView,
    StrategieEntfernenView,
)

app_name = 'strategie'
urlpatterns = [
    path('', StrategieListeView.as_view(), name='strategie-liste'),
    path('erstellen/', StrategieErstellenView.as_view(), name='strategie-erstellen'),
    path('<int:id>/', StrategieDetailView.as_view(), name='strategie-details'),
    path('<int:id>/bearbeiten/', StrategieBearbeitenView.as_view(), name='strategie-bearbeiten'),
    path('<int:id>/entfernen/', StrategieEntfernenView.as_view(), name='strategie-entfernen'),
]