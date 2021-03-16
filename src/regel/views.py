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
    appName             = appName
    model               = Regel
    elementeBezeichnung = "regeln"

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
    
    template_name = 'modulViews/generisch_detail.html'  
    appName       = appName
    model         = Regel 
    
class RegelBearbeitenView(bearbeitenViewMixin):
    """
        Klasse der Ansicht für das Bearbeiten einer existierenden Regel.
        """  

    template_name = 'modulViews/generisch_bearbeiten.html' 
    form_class    = RegelModelForm
    appName       = appName
    model         = Regel

class RegelEntfernenView(entfernenViewMixin):
    """
        Klasse der Ansicht für das Löschen einer Regel.
        """  

    template_name = 'modulViews/generisch_entfernen.html' 
    appName       = appName
    model         = Regel

class RegelFehlerView(fehlerViewMixin):
    """
        Klasse für das Anzeigen von jeglichen Fehlermeldungen.
        """  

    appName = appName