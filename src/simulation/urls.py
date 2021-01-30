from django.urls import path
from simulation.views import (
    SimulationErstellenView,
    SimulationErgebnisView,
    SimulationListeView,
    SimulationBearbeitenView,
    SimulationEntfernenView,
)


app_name = 'simulation'
urlpatterns = [
    path('erstellen/', SimulationErstellenView.as_view(), name="simulation-erstellen"),
    path('ergebnis/', SimulationErgebnisView.as_view(), name="simulation-ergebnis"),
   # path('test/', views.starter, name="starter")
    path('', SimulationListeView.as_view(), name='simulation-liste'),
    path('<int:id>/bearbeiten/', SimulationBearbeitenView.as_view(), name='simulation-update'),
    path('<int:id>/entfernen/', SimulationEntfernenView.as_view(), name='simulation-entfernen'),
]