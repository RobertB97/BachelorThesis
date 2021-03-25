from django.urls      import path
from simulation.views import (
    SimulationConfigView,
    SimulationErgebnisView,
    downloadCSV,
    SimulationFehlerView,
)

#URL Dispatch für Simulation-App

app_name    = 'simulation'
urlpatterns = [
    path('',          SimulationConfigView.as_view(),   name="simulation-config"),
    path('ergebnis/', SimulationErgebnisView.as_view(), name="simulation-ergebnis"),
    path('fehler/',   SimulationFehlerView.as_view(),   name="simulation-fehler"),
    path('download/', downloadCSV,                      name="download-simulation-ergebnis")
]