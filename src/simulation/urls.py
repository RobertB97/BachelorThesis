from django.urls import path
from simulation.views import (
    SimulationHinzufuegenView,
    SimulationErgebnisView,
    SimulationListeView,
    SimulationBearbeitenView,
    SimulationEntfernenView,
)


app_name = 'simulation'
urlpatterns = [
    path('hinzufuegen/', SimulationHinzufuegenView.as_view(), name="simulation-hinzufuegen"),
    path('ergebnis/', SimulationErgebnisView.as_view(), name="simulation-ergebnis"),
   # path('test/', views.starter, name="starter")
    path('', SimulationListeView.as_view(), name='simulation-liste'),
    path('<int:id>/bearbeiten/', SimulationBearbeitenView.as_view(), name='simulation-update'),
    path('<int:id>/entfernen/', SimulationEntfernenView.as_view(), name='simulation-entfernen'),
]