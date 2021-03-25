from django.contrib import admin
from .models        import Simulation

# Hier wird das Simulation model für den Admin Panel verfügbar. 

admin.site.register(Simulation)