from django.urls import path
from regel.views import (
    RegelErstellenView,
    RegelListeView,
    RegelDetailView,
    RegelBearbeitenView,
    RegelEntfernenView,
)


app_name = 'regel'
urlpatterns = [
    path('', RegelListeView.as_view(), name='regel-liste'),
    path('erstellen/', RegelErstellenView.as_view(), name='regel-erstellen'),
    path('<int:id>/', RegelDetailView.as_view(), name='regel-detail'),
    path('<int:id>/bearbeiten/', RegelBearbeitenView.as_view(), name='regel-bearbeiten'),
    path('<int:id>/entfernen/', RegelEntfernenView.as_view(), name='regel-entfernen'),
]
