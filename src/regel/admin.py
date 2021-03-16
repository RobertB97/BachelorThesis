from django.contrib import admin

from .models import Regel

# Hier wird das Regel model für den Admin Panel verfügbar. 

admin.site.register(Regel)