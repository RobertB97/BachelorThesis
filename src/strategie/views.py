# django imports
from django.shortcuts import  redirect, reverse

from trading.mixins import (
    listenViewMixin,
    hinzufuegenViewMixin,
    detailViewMixin,
    bearbeitenViewMixin,
    entfernenViewMixin,
    fehlerViewMixin,
    allgemeineFehlerPruefung,
    datenAnBackendSenden,
)
# Regel app import
from regel.models import Regel

# Strategie app imports
from .forms  import StrategieModelForm
from .models import Strategie

appName           = "strategie"

class getContextMixin:
    """
        Klasse, welche die get_context_data Funktion zur verfügung stellt. Diese Funktion 
        ist bei StrategieDetailView, StrategieBearbeitenView und StrategieEntfernenView identisch.

    """
    def get_context_data(self, *args, **kwargs):
        """
            Holt die Daten aller Regeln. Die Daten der verwendeten Regel werden in eine eigene Liste gespeichert.

        """
    
        context   = super().get_context_data(**kwargs)   
        
        # Daten an Backend senden.
        serverAntwort = datenAnBackendSenden(
            hauptPfad = "regel/", 
            unterPfad = "getalle", 
            daten     = {"benutzer_id": self.request.user.username}
        )

        # ServerAntwort auf Fehler prüfen. Bei gefundenen Fehler auf FehlerSeite leiten.
        if(allgemeineFehlerPruefung(serverAntwort, self.request)):
            return redirect(reverse("strategie:strategie-fehler"))
        
        verwendeteRegelListe = []

        # Liste mit verwendeten Regeln erstellen.
        for regel in serverAntwort["regeln"]:
            if(regel["id"] in self.request.session["verwendete-regeln"]):
                verwendeteRegelListe.append(regel)

        # Alle Regeln im Context speichern
        context["regeln"]           = serverAntwort["regeln"]
        # Alle verwendeten Regeln im Context speichern
        context["verwendeteRegeln"] = verwendeteRegelListe
        # Den bearbeitbar-Wert in Context speichern. Wichtig für DetailAnsicht
        context["bearbeitbar"]      = self.request.session["bearbeitbar"]
        return context

class StrategieListeView(listenViewMixin):
    """
        Klasse für das Darstellen der Strategien in einer Liste.
        """  

    appName             = appName

class StrategieHinzufuegenView(hinzufuegenViewMixin):
    """
        Klasse für das Erstellen/ Hinzufügen von neuen Strategien.

        Methoden
        ------
        """   
            
    form_class    = StrategieModelForm
    appName       = appName
    model         = Strategie
    neuErstellen  = True

    def get(self, request, *args, **kwargs):
        """
            Holt alle verfügbaren Regeln für die Darstellung.

            Hier wird die get_context_data-Funktion der CreateView-Klasse überschrieben.
            Es wird mit datenAnBackendSenden versucht die Daten zu holen. 
            Auf die dabei potentiell entstandenen Fehler wird in allgemeineFehlerPruefung geprüft.
            Bei vorhandenen Fehlern wird von der Funktion ein True zurückgegeben
            was zu einem Redirect auf die FehlerView führt. Bei False wird die 
            serverAntwort im Context gespeichert, um eine Darstellung der Regeln zu ermöglichen"""
        serverAntwort = datenAnBackendSenden(
            hauptPfad = "regel/",
            unterPfad = "getalle", 
            daten     = {
            "benutzer_id" : self.request.user.username,
            }
        )

        if(allgemeineFehlerPruefung(serverAntwort, self.request)):
            return redirect(reverse("strategie:strategie-fehler"))

        self.object = Strategie()
        context     = self.get_context_data(object=self.object)
        context["regeln"] = serverAntwort["regeln"]
        context["appName"] = appName
        return self.render_to_response(context)

class StrategieDetailView(getContextMixin, detailViewMixin):
    """
        Klasse für das Darstellen einer einzelnen Strategie.
        """  

    template_name = "strategie/strategie_detail.html" 
    appName       = appName
    model         = Strategie

class StrategieBearbeitenView(getContextMixin, bearbeitenViewMixin):
    """
        Klasse für das Bearbeiten einer existierendenStrategien.
        """  

    template_name = "strategie/strategie_bearbeiten.html"  
    form_class    = StrategieModelForm
    appName       = appName
    model         = Strategie
    
class StrategieEntfernenView(getContextMixin, entfernenViewMixin):
    """
        Klasse für das Löschen einer Strategie.
        """  

    template_name = "strategie/strategie_entfernen.html" 
    appName       = appName
    model         = Strategie

class StrategieFehlerView(fehlerViewMixin):
    """
        Klasse für das Anzeigen von jeglichen Fehlermeldungen.
        """

    appName       = appName