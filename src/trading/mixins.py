import requests
import json

from django.conf            import settings
from django.shortcuts       import redirect, reverse

from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    TemplateView,
)
class renderObjectHolenMixin:
    """
        Klasse zuständig für das Holen von einzelnen Objekten und Umwandeln deren in renderbare Objekte.
    """
    appName             = None
    model               = None
    leerzeichenErsetzen = None
    istDetailView       = None
    
    def get(self, request, **kwargs):
        """
            Holt das renderbare Objekt mit den entsprechenden Daten für die Darstellung mithilfe der Funktion renderObjekt().

            """
        objektZumRender = renderObjekt(
            callerSelf          = self, 
            objekttyp           = self.appName, 
            model               = self.model, 
            hauptPfad           = self.appName + "/", 
            fehlerSeite         = self.appName + ":" + self.appName + "-fehler",
            leerzeichenErsetzen = self.leerzeichenErsetzen,
        )
        # Objekt wird zurückgegeben wenn renderObjectHolenMixin vom DetailView aufgerufen wird, oder wenn es bearbeitbar ist. 
        # Bearbeitbar-Attribut ist wichtig für die Bearbeiten- und Entfernen-Ansicht
        if(self.istDetailView):
            return objektZumRender
        if(self.request.session["bearbeitbar"] == True):
            return objektZumRender
        return redirect("../")

class listenViewMixin(ListView):
    """
    Verallgemeinerte Listen Anisicht. 
    Verwendet das template "modulViews/generisch_liste.html".
    Holt die entsprechenden Daten für die Listenansicht und wandelt sie in das benötigte Format.
    """
    template_name       = "modulViews/generisch_liste.html"
    appName             = None
    model               = None
    elementeBezeichnung = None

    def get_context_data(self, *args, **kwargs):
        """
        Zuständig für das Bereitstellen von Context Date im Template. 
        Hier wird der appName an das Template weitergegeben.
        """
        context            = super().get_context_data(**kwargs)  
        context["appName"] = self.appName
        return context

    def get(self, request, *args, **kwargs):
        """
            Holt alle Objekte für die ListenAnsicht.

            Löscht alle Modul Objekte, welche in der SQLite gespeichert sind. 
            Diese Objekte werden von Django beispielsweise beim HinzufuegenView automatisch erstellt. 
            Da die Elemente bereits in der Backend DB gespeichert werden, ist eine weitere Speicherung redundant.
            Dann wird versucht die Daten vom Backend mit datenAnBackendSenden() zu holen, 
            dabei kann entweder ein JSON mit den benötigten Daten,ein JSON mit der Fehlermeldung die im Backend entstanden ist 
            oder der String "KeineVerbindung" zurückgegeben.
            Mit der Methode allgemeineFehlerPruefung werden beide Fehlerquellen geprüft und wenn zutreffend, ein True zurückgegeben, sonst False.
            Bei True wird eine Weiterleitung auf die Fehlerseite ausgeführt; 
            bei False wurde kein Fehler gefunden, d.h. die Antwort des Backends beinhaltet die benötigten Daten.
            Die Objekte in den Daten werden in das QuerySet von ListeView, welches eine Auflistung in der UI ermöglicht.
            Mit super.get() wird diese Funktion im allgemeinen Klassen-Kontext aufgerufen um Zugang zu den Daten außerhalb der Funktion zu erhalten.
            """
        
        unterPfad     = "getalle"
        daten         = {
            "benutzer_id" : self.request.user.username,
        }
        serverAntwort = datenAnBackendSenden(self.appName+"/", unterPfad, daten)

        if(allgemeineFehlerPruefung(serverAntwort, request)):
            return redirect(reverse(self.appName + ":" + self.appName + "-fehler")) #appName:appName-fehler
        
        self.queryset = serverAntwort[self.elementeBezeichnung]
        return super().get(request, *args, **kwargs)

class hinzufuegenViewMixin(CreateView):
    """
    Verallgemeinerte Hinzufuegen Anisicht. 
    Verwendet das template "modulViews/generisch_hinzufuegen.html".
    Holt die entsprechenden Daten für die Listenansicht und wandelt sie in das benötigte Format.
    """

    template_name = "modulViews/generisch_hinzufuegen.html"
    form_class    = None
    appName       = None
    model         = None
    neuErstellen  = None # Mixin kann von Bearbeiten Ansicht aufgerufen. 
    # Um anzugeben, dass kein neues Objekt in der DB zu erstellen werden soll, wird das Attribut neuErstellen verwendet. 

    def get(self, request, *args, **kwargs):
        """
        Testet die Verbindung zum Backend. Wenn keine Verbindung vorhanden, wird auf die FehlerSeite weitergeleitet.
        Ansonsten wird das für das Context-Objekt ein leere Modelinstanz gegeben und der appName im Context gespeichert.
        Die Werte der einzelnen Modelinstanz Felder werden in das Formular eingetragen. Es darf also keine Daten enthalten.
        """
        queryset = requests.post(settings.BACKEND_URL)
        if(queryset.status_code == 404):
            return redirect(reverse(self.appName + ":" + self.appName + "-fehler")) #appName:appName-fehler

        self.object = self.model() 
        context     = self.get_context_data()
        context["appName"] = self.appName
        return self.render_to_response(context)

    def form_valid(self, form):
        """
            Schickt die Objektdaten an die API.

            Wird automatisch nach erfolgreichem Ausfüllen und Abschicken des Formulars aufgerufen. 
            Die neuen Daten werden an die Funktion allgemeinesFormValid() weitergeben, welche das Abschicken an die API übernimmt.
            Das Dictionary mit den neuen Daten wird abhängig von der App zusammengebaut. 
            """
        daten     = {
            "benutzer_id"            : self.request.user.username,
            "name"                   : form.cleaned_data["name"],
            "beschreibung"           : form.cleaned_data["beschreibung"],
        }
        if(self.neuErstellen): # neuErstellen == True 
            unterPfad   = "hinzufuegen"
        else:# neuErstellen == False 
            daten["id"] = self.kwargs.get("id")
            unterPfad   = "bearbeiten"

        if(self.appName == "indikator"):
            daten["eigene_skala"]           = form.cleaned_data["eigene_skala"]
            daten["berechnung_pseudo_code"] = form.cleaned_data["berechnung_pseudo_code"]

        if(self.appName == "regel"):
            daten["berechnung_pseudo_code"] = form.cleaned_data["berechnung_pseudo_code"]

        if(self.appName == "strategie"):
            regelListe        = form.cleaned_data["regeln"].split(",")
            #Wandelt die RegelID-Strings in Zahlen um, sonst werden die Daten von der API nicht akzeptiert
            regelListeMitInts = [ int(regel) for regel in regelListe ] 
            daten["regeln"]   = regelListeMitInts

        return allgemeinesFormValid(
            hauptPfad   = self.appName + "/", 
            unterPfad   = unterPfad, 
            daten       = daten, 
            request     = self.request,
            fehlerSeite = self.appName + ":" + self.appName + "-fehler"
        )

class detailViewMixin(renderObjectHolenMixin,DetailView):
    """
    Verallgemeinerte Detail Anisicht. 
    Baut auf renderObjectHolenMixin und DetailView auf, aber gewisse Eigenschaften werden hier bereits festgelegt.
    Diese Eigenschaften sind:
        - leerzeichenErsetzen = True => Leerzeichen sollen durch &nbsp ersetzt werden.
        - istDetailView = True => RenderObjekt muss nicht bearbeitbar sein, damit es von renderObjectHolenMixin zurückgegeben wird.
    Hat die zusätzliche Methode get_context_data.
    """
    template_name       = None
    appName             = None
    model               = None
    hauptPfad           = None
    leerzeichenErsetzen = True
    istDetailView       = True

    def get_context_data(self, *args, **kwargs):
        """
        Zuständig für das Bereitstellen von Context Date im Template. 
        Hier wird der bearbeitbar-Zustand an das Template weitergegeben.
        """
        context                = super().get_context_data(**kwargs)  
        context["bearbeitbar"] = self.request.session["bearbeitbar"]
        return context

class bearbeitenViewMixin(renderObjectHolenMixin,hinzufuegenViewMixin):
    """
    Verallgemeinerte Bearbeiten Anisicht. 
    Baut auf renderObjectHolenMixin und hinzufuegenViewMixin auf, aber gewisse Eigenschaften werden hier bereits festgelegt.
    Diese Eigenschaften sind:
        - neuErstellen = False => es soll kein neues Objekt angelegt werden, sondern ein bereits existierendes angepasst werden.
        - leerzeichenErsetzen = False => Leerzeichen sollen nicht durch &nbsp ersetzt werden.
        - istDetailView = False => RenderObjekt muss bearbeitbar sein, damit es von renderObjectHolenMixin zurückgegeben wird.
    """
    template_name       = None
    form_class          = None
    appName             = None
    model               = None
    neuErstellen        = False
    leerzeichenErsetzen = False
    istDetailView       = False

class entfernenViewMixin(renderObjectHolenMixin, DeleteView):
    """
    Verallgemeinerte Entfernen Anisicht. 
    Baut auf renderObjectHolenMixin und DeleteView auf, aber gewisse Eigenschaften werden hier bereits festgelegt.
    Diese Eigenschaften sind:
        - leerzeichenErsetzen = True => Leerzeichen sollen durch &nbsp ersetzt werden.
        - istDetailView = False => RenderObjekt muss bearbeitbar sein, damit es von renderObjectHolenMixin zurückgegeben wird.
    """
    template_name       = None
    appName             = None
    model               = None
    leerzeichenErsetzen = True
    istDetailView       = False

    def post(self, request, *args, **kwargs):
        """
            Schickt die Daten des zu löschenden Objekts an die API.
            
            Die Funktion wird bei POST-Requests auf die EntfernenView aufgerufen.
            Die Daten des zu löschenden Objekts weitergegeben an datenAnBackendSenden(), welches die Daten an das Backend sendet.
            Die Funktion kann entweder ein JSON mit dem gelöschten Objekt als Bestätigung, ein JSON mit der Fehlermeldung die im Backend entstanden ist 
            oder der String "KeineVerbindung" zurückgegeben.
            Mit der Methode allgemeineFehlerPruefung werden beide Fehlerquellen geprüft und wenn zutreffend, ein True zurückgegeben, sonst False.
            Bei True wird eine Weiterleitung auf die entsprechende Fehlerseite ausgeführt; 
            bei False wurde kein Fehler gefunden, d.h. das Objekt konnte erfolgreich gelöscht werden. 
            Somit wird ein Redirect auf die entsprechende ListenAnsicht zurückgegeben. """

        serverAntwort = datenAnBackendSenden(
            hauptPfad = self.appName + "/", 
            unterPfad = "loeschen", 
            daten     = {
                "id"         : self.kwargs.get("id"),
                "benutzer_id": self.request.user.username,
            }
        )

        if(allgemeineFehlerPruefung(serverAntwort, request)):
            return redirect(reverse(self.appName + ":" + self.appName + "-fehler"))  #appname:appname-fehler

        return redirect(reverse(self.appName + ":" + self.appName + "-liste")) #appname:appname-liste  

class fehlerViewMixin(TemplateView):
    """
    Verallgemeinerte Fehler Anisicht. 
    """
    appName       = None
    template_name = "modulViews/generisch_fehler.html"

    def get(self, request):
        """
            Holt das Fehlermeldung die angezeigt werden soll.

            Die in der Session gespeicherte Fehlermeldung wird geholt und an die Darstellung weitergegeben
            Wenn die Fehlermeldung leer ist, versucht der Nutzer manuell auf die Fehlerseite zu kommen. 
            Da kein Fehler vorhanden ist, wird auf die ListenAnsicht weitergeleitet"""

        context            = self.get_context_data()
        context["fehler"]  = request.session["fehler"]
        context["appName"] = self.appName

        
        if(request.session["fehler"] == ""):
            if(self.appName == "simulation"):
                return redirect(reverse(self.appName + ":" + self.appName + "-config")) #appname:appname-liste
            else:
                return redirect(reverse(self.appName + ":" + self.appName + "-liste")) #appname:appname-liste
        
        return self.render_to_response(context)

def datenAnBackendSenden(hauptPfad, unterPfad, daten):
    """
        Funktion, die das Zusammenbauen des URLS und das Abschicken an das Backend übernimmt.
            
        Der Domain-Teil teil wird von settings.BACKEND_URL geholt. 
        Der Hauptpfad und Unterpfad werden beim Funktion aufruf definiert. 
        Wenn die Serverantwort den Status Code 404 hat, konnte keine Verbindung aufgebaut werden und der String "KeineVerbindung" wird zurückgegeben
        Ansonsten wird ein JSON mit den Backend Daten zurückgegeben,

        Parameter
        ----------
        hauptPfad : string     
            Der HauptPfad der API an den die Daten geschickt werden sollen
        unterPfad : string     
            Der Unterpfad der API an den die Daten geschickt werden sollen
        daten : dict
            Die Daten die an das Backend geschickt werden sollen  


        Rückgabewerte
        ----------
        string
            String mit dem Wert "KeineVerbindung", wenn keine Verbindung zum Server aufgebaut werden konnte
        JSON
            Serverantwort    """
    queryset = requests.post(
        url  = settings.BACKEND_URL + hauptPfad + unterPfad, 
        json = daten
    )
    if(queryset.status_code == 404):
        return "KeineVerbindung" 
    return json.loads(queryset.text)

def allgemeinesFormValid(hauptPfad, unterPfad, daten, request, fehlerSeite):
    """
        Verallgemeinerte Funktion für das Verarbeiten der Formulardaten

        Hier werden die Daten an das Backend mit datenAnBackendSenden() geschickt und die Antwort des Backends mit allgemeineFehlerPruefung() auf Fehler geprüft.
        Wenn fehlerfrei, im URL auf eine Ebene zurück weiterleiten. Dies ist die Detailansicht eines Elements
        (diese Methode kann nur vom BearbeitenView oder HinzufuegenView aufgerufen werden, daher ist die Ebene zurück der DetailView).
        Bei Fehlern wird auf die FehlerView weitergeleiten.

        Parameter
        --------
        hauptPfad : string
            der Hauptpfad der API an den die Daten geschickt werden sollen
        unterPfad : string
            der Unterpfad der API an den die Daten geschickt werden sollen
        daten : dict
            die Daten die an das Backend geschickt werden sollen
        request : object     
            die request-Instanz, wird bei der allgemeinenFehlerPruefung benötigt
        fehlerseite : string
            Fehlerseite auf die weitergeleitet wird, wenn Fehler gefunden.

        Rückgabewerte
        ----------
        redirect (normal)
            redirect auf eine Ebene im URL zurück
        redirect (bei Fehlern)
            redirect auf FehlerView   
        """

    if(allgemeineFehlerPruefung(
        serverAntwort = datenAnBackendSenden(hauptPfad, unterPfad, daten), 
        request = request)
    ):
        return redirect(reverse(fehlerSeite))  
    return redirect('../') 

def allgemeineFehlerPruefung(serverAntwort, request):
    """
        Verallgemeinerte Funktion für das Prüfen auf Fehler
        
        Wenn die serverAntwort "KeineVerbindung" ist, konnte keine Verbindung zur API aufgebaut werden.
        In der session wird die Fehlermeldung gespeichert und der Wert True zurückgegeben 
        (damit der FehlerView auf die Fehlermeldung zugreifen kann, muss sie in der session gespeichert werden).
        Ansonsten konnte eine Verbindung zur API aufgebaut werden und als nächstes wird auf vom Backend generierte Fehler geprüft 
        (Das zurückgegebene JSON würde hier den key Fehler enthalten). 
        Wenn in der Serverantwort ein Fehler enthalten ist, wird dieser als Fehlermeldung in der session gespeichert und True zurückgegeben.
        Ansonsten wurden sowohl keine VerbindungsFehler oder Backend-Fehler gefunden werden.
        Die Fehlermeldung in der Session wird zurückgesetzt und ein False wird zurückgegeben. 
        Bei leeren Fehlermeldungen wird die FehlerView auf die ListenView weiterleiten.
        Der einzige Fall, bei dem keine Fehlermeldung vorhanden ist und es einen Zugriff auf die FehlerView gibt, 
        ist wenn der Nutzer manuell auf die Seite gehen würde.

        Parameter
        --------
        serverAntwort  : string | JSON
            Die zu prüfende Serverantwort.

        request : object
            Die Instanz des request Objekts der aufrufenden Klasse.
        
        Rückgabewerte
        ----------
        boolean 
            True wenn Fehler gefunden, sonst False    """
    if(serverAntwort == "KeineVerbindung"):
            request.session["fehler"] = "Fehlende Verbindung zum API Server"     
            return True       
    else:
        if("Fehler" in serverAntwort):
            request.session["fehler"] = serverAntwort["Fehler"]
            return True
    request.session["fehler"] = ""
    return False

def renderObjekt(callerSelf, objekttyp, model, hauptPfad, fehlerSeite, leerzeichenErsetzen):
    """
        Erstellt ein renderbares Regelobjekt oder gibt einen Redirect auf die Fehlerseite.

        Versucht mit datenAnBackendSenden() sich die Daten des zu renderenden Objekts zu holen. 
        Abhängig von allgemeineFehlerPruefung wird entweder ein Redirect zurückgegeben oder
        die Daten in der Serverantwort werden in ein Regelobjekt geschrieben, welches für die Darstellung benötigt wird. 
        Dabei werden die Werte der Keys, die im Daten-JSON und auch in dem Regelobjekt enthalten sind, 
        an die entsprechende Stelle in das Regelobjekt geschrieben.

        Parameter
        --------
        callerSelf : object
            Die self-Instanz der aufrufenden Klasse.
        objekttyp : string
            Der typ des Objekts, also entwedeer "indikator", "regel", oder "strategie"
        model : object
            Das Model der App, für die das zu rendernden Objekt erstellt werden soll. 
        hauptPfad : string
            der Hauptpfad der API an den die Daten geschickt werden sollen
        fehlerSeite : string
            Fehlerseite auf die weitergeleitet wird, wenn Fehler gefunden.
        leerzeichenErsetzen : boolean
            legt fest ob die Leerzeichen im Code durch &nbsp ersetzt werden soll. Wird bei manchen Darstellungen benötigt.


        Rückgabewerte
        ----------
        redirect (bei Fehlern)
            Ein Redirect auf die FehlerView.

        funktionsaufruf
            Es wird callerSelf.render_to_response(context) zurückgegeben, welches für die Darstellung des Objekts aufgerufen wird. """
    serverAntwort = datenAnBackendSenden(
        hauptPfad = hauptPfad,
        unterPfad = "get", 
        daten     = {
        "id"          : callerSelf.kwargs.get("id"),
        "benutzer_id" : callerSelf.request.user.username,
        }
    )
    if(allgemeineFehlerPruefung(serverAntwort, callerSelf.request)):
        return redirect(reverse(fehlerSeite))

    if(serverAntwort[objekttyp]["benutzer_id"] == "superuser"):
        if(callerSelf.request.user.username == "superuser"):
            callerSelf.request.session["bearbeitbar"] = True
        else:            
            callerSelf.request.session["bearbeitbar"] = False
    else:
        callerSelf.request.session["bearbeitbar"] = True


    objektFuerDarstellung = model()
    for key in serverAntwort[objekttyp].keys():  
        if key in dir(objektFuerDarstellung):
            setattr(objektFuerDarstellung, key, serverAntwort[objekttyp][key])
    if(leerzeichenErsetzen):
        # Wenn objekttyp indikator oder regel und leerzeichenErsetzen true, Leerzeichen mit &nbsp ersetzen
        if(objekttyp == "indikator" or objekttyp == "regel"):
            setattr(objektFuerDarstellung, "berechnung_pseudo_code", objektFuerDarstellung.berechnung_pseudo_code.replace(" ","&nbsp")) #Leerzeichen mit HTML-code für Leerzeichen ersetzen
            setattr(objektFuerDarstellung, "berechnung_pseudo_code", objektFuerDarstellung.berechnung_pseudo_code.replace("	","&nbsp&nbsp&nbsp&nbsp")) #Tabulator durch 4 HTML-Leerzeichen ersetzen
    
    if(objekttyp == "strategie"):
        callerSelf.request.session["verwendete-regeln"] = serverAntwort[objekttyp]["regeln"]


    callerSelf.object  = objektFuerDarstellung
    context            = callerSelf.get_context_data(object = callerSelf.object)
    context["appName"] = objekttyp
    return callerSelf.render_to_response(context)

