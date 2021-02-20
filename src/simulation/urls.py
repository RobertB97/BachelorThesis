from django.urls import path
from simulation.views import (
    SimulationConfigView,
    SimulationErgebnisView,
    SimulationReconfigView,
)


app_name = 'simulation'
urlpatterns = [
    path('', SimulationConfigView.as_view(), name="simulation-config"),
    path('ergebnis/', SimulationErgebnisView.as_view(), name="simulation-ergebnis"),
    path('reconfig/', SimulationReconfigView.as_view(), name='simulation-reconfig'),
]