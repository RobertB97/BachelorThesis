from django.contrib import admin
from .models import Indikator

# Hier wird das Indikator model für den Admin Panel verfügbar. 

admin.site.register(Indikator)