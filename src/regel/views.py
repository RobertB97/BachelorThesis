# Mixin imports
from trading.mixins import (
    listenViewMixin,
    hinzufuegenViewMixin,
    detailViewMixin,
    bearbeitenViewMixin,
    entfernenViewMixin,
    fehlerViewMixin
)
# Regel app imports
from .forms  import RegelModelForm
from .models import Regel

appName = "regel"

class RegelListeView(listenViewMixin):
    """
        Klasse der Ansicht für das Darstellen der Regeln in einer Liste.
        """  
    appName = appName
    model   = Regel

class RegelHinzufuegenView(hinzufuegenViewMixin): 
    """
        Klasse der Ansicht für das Erstellen/ Hinzufügen von neuen Regeln.
        """    

    form_class    = RegelModelForm
    appName       = appName
    model         = Regel
    neuErstellen  = True
    
class RegelDetailView(detailViewMixin):
    """
        Klasse der Ansicht für das Darstellen einer einzelnen Regel.
        """  
    
    appName       = appName
    model         = Regel 
    
class RegelBearbeitenView(bearbeitenViewMixin):
    """
        Klasse der Ansicht für das Bearbeiten einer existierenden Regel.
        """  

    form_class    = RegelModelForm
    appName       = appName
    model         = Regel

class RegelEntfernenView(entfernenViewMixin):
    """
        Klasse der Ansicht für das Löschen einer Regel.
        """  

    appName       = appName
    model         = Regel

class RegelFehlerView(fehlerViewMixin):
    """
        Klasse für das Anzeigen von jeglichen Fehlermeldungen.
        """  

    appName = appName