# allgemeine imports
import csv
import itertools
from datetime import datetime
from math     import pi

import pandas as pd

# bokeh imports
from bokeh.embed    import components
from bokeh.layouts  import column
from bokeh.models   import Panel, Tabs
from bokeh.palettes import Dark2_5 as palette
from bokeh.plotting import figure

# django imports
from django.conf          import settings
from django.http          import HttpResponse
from django.shortcuts     import redirect, render, reverse
from django.views         import View
from django.views.generic import CreateView, TemplateView

from trading.mixins import (
    fehlerViewMixin,
    allgemeineFehlerPruefung,
    datenAnBackendSenden,
)

# Strategie app imports
from strategie.models import Strategie

# Simulation app imports
from .forms  import SimulationModelForm
from .models import Simulation

globalerHauptPfad = "simulation"
appName           = "simulation"

class SimulationFehlerView(fehlerViewMixin):
    """
        Klasse für das Anzeigen von jeglichen Fehlermeldungen.
        """  

    appName = appName

class SimulationConfigView(CreateView): 
    """
        Klasse der Ansicht für das Konfigurieren einer Simulation.

        Methoden
        --------
        get 
            Holt alle benötigten Daten.
        form_valid
            Schickt Eingabedaten an Backend und prüft auf Fehler.
        """  
    form_class    = SimulationModelForm
    template_name = 'simulation/simulation_config.html'
       

    def get(self, request, *args, **kwargs):
        """ 
        Hier werden alle benötigten Daten für das Konfigurieren einer Simulation geholt. Dazu gehören alle verfügbaren Strategien 
        und alle verfügbaren finanziellen Instrumente, auf denen eine Simulation laufen kann. 
        Diese werden an das Template über den Context weitergegeben. Die getroffene Wahl wird über JavaScript in das entsprechende Formular Feld geschrieben
        """
        Simulation.objects.all().delete() # Alle erstellten Objekte löschen. Diese werden temporär erstellt um verlustfreies Anzeigen von Daten zu garantieren

        self.object  = None # CreateView braucht irgendein Object, None ist dabei ein valider Wert
        context      = super().get_context_data(**kwargs) 

        # Hier werden alle Strategie-Daten bezogen.
        serverAntwort = datenAnBackendSenden(
            hauptPfad = "strategie/", 
            unterPfad = "getalle", 
            daten = {
                "benutzer_id" : request.user.username,
            }
        )
        # Wenn Fehler enthalten, auf FehlerSeite weiterleiten, ansonsten Strategie Daten im Context speichern.
        if(allgemeineFehlerPruefung(serverAntwort,request)):
            return redirect(reverse('simulation:simulation-fehler'))  
        context['strategien'] = serverAntwort["strategien"]
        # ------------------------
        
        # Hier werden alle ISIN-Daten bezogen.
        serverAntwort = datenAnBackendSenden(
            hauptPfad = "isin/", 
            unterPfad = "getalle", 
            daten = {
                "benutzer_id": request.user.username,
            }
        )
        if(allgemeineFehlerPruefung(serverAntwort,self.request)):
            return redirect(reverse('simulation:simulation-fehler'))  
        
        alleIsins = []
        """ 
        Die ISINs können Indizes und Währungen enthalten. 
        Indices können anhand zwei verschiedener Attribute (ist_index == True und einheit == "Punkte") identifiziert werden
        Währungen können anhand der Einheit identifiziert werden (einheit == "undefiniert")
        Alle ISINs die nicht diese Attribute haben, werden in eine separate Liste gespeichert und schließlich im Context gespeichert
        """
        for isin in serverAntwort["isins"]:
            if(not isin["ist_index"] and isin["einheit"] != "Punkte" and isin["einheit"] != "undefiniert"):
                alleIsins.append(isin)
                
        serverAntwort["isins"] = alleIsins
        context['isins'] = serverAntwort["isins"]
        # ------------------------
        return self.render_to_response(context)

    def form_valid(self, form):
        """
        Hier werden die Eingabedaten des Nutzers an das Backend gesendet. 
        Wenn dabei Fehler entstanden sind, wird auf die Fehlerseite weitergeleitet. 
        Ansonsten wird mit dem return von super.form_valid automatisch ein Simulations-Objekt erstellt, get_absolute_url des Objekts aufgerufen und
        somit auf die Simulations-Ergebnis-Ansicht weitergeleitet.

        """
        simulationsDaten = datenAnBackendSenden(
            hauptPfad = globalerHauptPfad, 
            unterPfad = "", 
            daten     = {
                "benutzer_id"   : self.request.user.username,
                "strategie_id"  : int(form.cleaned_data["strategie"]),
                "isin"          : form.cleaned_data["isin"],
                "start_kapital" : int(form.cleaned_data["startkapital"]),
                "start_datum"   : str(form.cleaned_data["von_datum"]),
                "end_datum"     : str(form.cleaned_data["bis_datum"])
            }
        )

        if(allgemeineFehlerPruefung(simulationsDaten, self.request)):
            return redirect(reverse('simulation:simulation-fehler'))  
        else:
            self.request.session["simulationsDaten"] = simulationsDaten
            return super().form_valid(form) 

class SimulationErgebnisView(View):
    """
    Klasse der Ansicht für das Darstellen des Simulations-Ergebnis.

    Methoden
    --------
    get
        Zuständig für das Holen und Darstellen der Ergebnis-Daten.
    """

    template_name = 'simulation_ergebnis.html'

    def get(self, request):
        """
        Diese Funktion holt sich alle Daten die benötigt werden für das Darstellen der Simulations-Ergebnisse.
        Dazu gehören die Aktienkurs Daten der zum simulieren verwendeten ISIN und die Simulationsergebnisse.

        """
        simulationsObject = Simulation.objects.last() # Zuletzt erstelltes Objekt holen
        if(simulationsObject == None): # Prüfen ob es existiert, wenn nicht, auf FehlerSeite weiterleiten und entsprechende Fehlermeldung in session speichern.
            request.session["fehler"] = "Keine Simulationsdaten vorhanden"     
            return redirect(reverse('simulation:simulation-fehler')) 
        
        # Hier werden die Simulation-Konfigurations-Daten an das Backend geschickt.
        simulationsDaten = datenAnBackendSenden(
            hauptPfad = globalerHauptPfad, 
            unterPfad = "", 
            daten     = {
                "benutzer_id"   : self.request.user.username,
                "strategie_id"  : int(simulationsObject.strategie),
                "isin"          : simulationsObject.isin,
                "start_kapital" : int(simulationsObject.startkapital),
                "start_datum"   : str(simulationsObject.von_datum),
                "end_datum"     : str(simulationsObject.bis_datum)
            }
        )
        # Bei Fehlern auf Fehlerseite weiterleiten
        if(allgemeineFehlerPruefung(simulationsDaten,request)):
            return redirect(reverse('simulation:simulation-fehler'))  
        #------------------

        self.request.session["simulationsDaten"] = simulationsDaten # Simulationsdaten in Session speichern um für die Funktion downloadCSV zugänglich zu machen
        
        #Von- und Bis-Datum in passendes Format TT.MM.JJJJ umwandeln
        vonDatumAnzeigeFormat = datetime.strptime(str(simulationsObject.von_datum), '%Y-%m-%d').strftime('%d.%m.%Y') 
        bisDatumAnzeigeFormat = datetime.strptime(str(simulationsObject.bis_datum), '%Y-%m-%d').strftime('%d.%m.%Y')

        # AnzeigeDaten Dict für Template zusammenbauen
        anzeigeDaten = {
            "strategie_id"   : int(simulationsObject.strategie),
            "strategie_name" : simulationsDaten["strategie"]["name"],
            "isin"           : simulationsDaten["wertpapier"]["isin"],
            "name"           : simulationsDaten["wertpapier"]["name"],
            "start_kapital"  : int(simulationsObject.startkapital),
            "start_datum"    : str(vonDatumAnzeigeFormat),
            "end_datum"      : str(bisDatumAnzeigeFormat),
            "statistik"      : simulationsDaten["strategie_statistik"],
        }

        # Statistischen Werte auf 3 Nachkommestellen kürzen
        anzeigeDaten["statistik"]["performance_gesamt"]   = '%.3f' % (float(anzeigeDaten["statistik"]["performance_gesamt"]))
        anzeigeDaten["statistik"]["performance_pro_jahr"] = '%.3f' % (float(anzeigeDaten["statistik"]["performance_pro_jahr"]))
        anzeigeDaten["statistik"]["hoch_gesamt"]          = '%.3f' % (float(anzeigeDaten["statistik"]["hoch_gesamt"]))
        anzeigeDaten["statistik"]["tief_gesamt"]          = '%.3f' % (float(anzeigeDaten["statistik"]["tief_gesamt"]))
        anzeigeDaten["statistik"]["maximum_drawdown"]     = '%.3f' % (float(anzeigeDaten["statistik"]["maximum_drawdown"]))

        # Alle Koordinatensysteme erstellen
        
        
        
        p1 = figure( # p1 ist Koordinatensystem mit Aktienkurs als Candlesticks
            plot_width=1000, 
            plot_height=700, 
            x_axis_type="datetime", 
            tools="pan, wheel_zoom, box_zoom, reset, save" # verfügbaren Tools
        )
        p2 = figure( # p2 ist Koordinatensystem mit Aktienkurs als Linie
            plot_width=1000, 
            plot_height=700, 
            x_axis_type="datetime", 
            tools="pan, wheel_zoom, box_zoom, reset, save", 
            x_range=p1.x_range, # Verschiebungen entlang der X-Achse von p1 übernehmen
            y_range=p1.y_range  # Verschiebungen entlang der Y-Achse von p1 übernehmen
        )
        p3 = figure( # p3 ist Koordinatensystem für Performance-Entwicklung
            plot_width=1000, 
            plot_height=700, 
            x_axis_type="datetime", 
            tools="pan, wheel_zoom, box_zoom, reset, save",
            x_range=p1.x_range # Verschiebungen entlang der X-Achse von p1 übernehmen
            # Verschiebung entlang der Y-Achse wird nicht übernommen, da es keinen Sinn ergibt.
        )
        plotListe = [p1,p2,p3] # Alle Koordinatensyteme in eine Liste

        indikatoren = simulationsDaten["indikator_zeitreihe"] # Alle indikatordaten werden in einem eigenen Objekt gespeichert
        keyList     = []
        listenDict  = {}

        print(indikatoren)
        # Jeder einzelne Key wird in die Key-Liste gespeichert und für jeden Key wird im ListenDict eine leere Liste erstellt.
        # Der erste key ist immer der Zeitstempel, die darauf folgenden sind die keys der Indikatoren
        for key in indikatoren[0]:
            keyList.append(key)
            listenDict[key] = []

        # daten im indikatoren-Objekt werden aufgeteilt und abhängig vom key an die entsprechende Liste im listenDict angefügt.
        for daten in indikatoren:
            for key in keyList:
                listenDict[key].append(daten[key])

        # Farb-Palette für das Darstellen der Graphen in verschiedenen Farben
        colors = itertools.cycle(palette)

        # Alle benötigten DataFrames generieren und deren Zeitstempel entsprechend formatieren
        zeitstempelDataFrame                = pd.DataFrame(listenDict["zeitstempel"], columns = ['zeitstempel'])
        zeitstempelDataFrame["zeitstempel"] = pd.to_datetime(zeitstempelDataFrame["zeitstempel"])

        kursZeitreiheDF                     = pd.DataFrame(simulationsDaten["kurs_zeitreihe"])
        kursZeitreiheDF["zeitstempel"]      = pd.to_datetime(kursZeitreiheDF["zeitstempel"])

        stratZeitreiheDF                    = pd.DataFrame(simulationsDaten["strategie_kurs_zeitreihe"])
        stratZeitreiheDF["zeitstempel"]     = pd.to_datetime(stratZeitreiheDF["zeitstempel"])

        kaufVerkaufDF                       = pd.DataFrame(simulationsDaten["strategie_kaeufe_verkaeufe_zeitreihe"])


        inc = kursZeitreiheDF.close > kursZeitreiheDF.open # inc ist ein boolean, welcher True zurückgibt wenn Close > Open
        dec = kursZeitreiheDF.open > kursZeitreiheDF.close # dec ist ein boolean, welcher True zurückgibt wenn Open > Close
        w = 12*60*60*1000  # halber Tag in ms, für die Breite der Kerzen

        # Hier werden die einzelnen Elemente der Kerze zum Koordinatensystem p1 hinzugefügt
        
        p1.segment( # Hier werden die High und Lows für jeden Tag erstellt, dargestellt durch zwei verbunde Punkte 
            kursZeitreiheDF.zeitstempel, # X Werte für Punkt 1
            kursZeitreiheDF.high,   # Y Werte für Punkt 1
            kursZeitreiheDF.zeitstempel, # X Werte für Punkt 2 
            kursZeitreiheDF.low, # Y Werte für Punkt 2
            color = "black"
        )
       
        p1.vbar(  # Hier werden die grünen Kerzen "Torsos" erstellt, dargestellt durch Balken je einem X-Wert, zwei Y-Werten und einer Breite
            kursZeitreiheDF.zeitstempel[inc], # X Werte der Balken 
            w, # Breite 
            kursZeitreiheDF.open[inc], # Y1 Werte der Balken
            kursZeitreiheDF.close[inc], # Y2 Werte der Balken
            fill_color = "green", line_color = "black"
        )
        
        p1.vbar(# Hier werden die roten Kerzen "Torsos" erstellt, dargestellt durch Balken je einem X-Wert, zwei Y-Werten und einer Breite
            kursZeitreiheDF.zeitstempel[dec], # X Werte der Balken 
            w, # Breite 
            kursZeitreiheDF.open[dec], # Y1 Werte der Balken
            kursZeitreiheDF.close[dec], # Y2 Werte der Balken
            fill_color = "red", line_color = "black"
        )
        # ---------------------------------
        
        p2.line( # Hier wird der Aktienkurs als Linie zu dem Koordinatensystem p2 hinzugefügt
            kursZeitreiheDF.zeitstempel, # X Werte der Linie
            kursZeitreiheDF.close, # Y Werte der Linie
            line_width = 3, color = "red", alpha = 0.5, 
            legend_label = simulationsDaten["wertpapier"]["name"] 
        ) 
        p3.line( # Hier wird die Performance als Linie zu dem Koordinatensystem p3 hinzugefügt
            stratZeitreiheDF.zeitstempel, 
            stratZeitreiheDF.kurs_prozentual, 
            line_width = 3, color = "black", alpha = 0.5, 
            legend_label = "Kapital in Prozent"
            )

        # Für jeden Key in der KeyListe
        for key in keyList:
            # Der nicht gleich zeitstempel, also für jeden Indikator
            if(key != "zeitstempel"):
                # wird ein eigenes DataFrame angelegt mit den entsprechenden Daten aus listenDict
                elementDataFrame = pd.DataFrame(listenDict[key])

                # Wenn Indikator eine eigene Skala braucht, wird ein neues Koordinatensystem erstellt
                inEigenesKoord = False
                if(pruefeObEigeneSkala(key,self)):
                    newPlot = figure(
                        plot_width=1000, 
                        plot_height=700, 
                        x_axis_type="datetime", 
                        tools="pan, wheel_zoom, box_zoom, reset, save",
                        x_range=p1.x_range # Verschiebungen entlang der X-Achse von p1 übernehmen
                    )
                    inEigenesKoord = True
                    
                # für jeden key in diesem DataFrame, also für jeden Graph des Indikators
                for i in listenDict[key][0].keys(): 
                    # wird eine eigene Linie erstellt mit den entsprechenden Y-Werten. Die X-Werte werden dabei vom ZeitstempelDataFrame übernommen,
                    # um es einheitlich zu halten
                    line = pd.concat(
                        [zeitstempelDataFrame, elementDataFrame[i]], axis=1)

                    # Wenn eigenes Koordianten System erstellt wurde, an dieses Koordinatensystem fügen 
                    if(inEigenesKoord):
                        newPlot.line(zeitstempelDataFrame["zeitstempel"], line[i],line_width=3, color=next(colors), alpha=1, legend_label=key+"-"+i)
                    
                    # Ansonsten in beide Koordinatensystemen p1 und p2 
                    else:
                        for plot in [p1,p2]:
                            plot.line(
                                zeitstempelDataFrame["zeitstempel"], 
                                line[i],
                                line_width=3, color=farbe, alpha=1, 
                                legend_label=key+"-"+i
                            )

                # Wenn eigenes Koordinatensystem erstellt wurde, dann dieses zur KoordinatenSystem Liste hinzufügen
                if(inEigenesKoord):
                    plotListe.append(newPlot)

        # Wenn das KaufVerkaufDataFrame nicht leer ist
        if(not kaufVerkaufDF.empty):
            # boolischen Ausdrücke generieren
            kauf    = kaufVerkaufDF.typ == "Kauf"
            verkauf = kaufVerkaufDF.typ == "Verkauf"

            # In beide Koordinatensystemen p1 und p2 werden die Markierungen für Käufe und Verkäufe eingefügt
            hauptPlotListe = [p1,p2]
            for plot in hauptPlotListe:
                plot.circle( # Punkte für Käufe
                    pd.to_datetime(kaufVerkaufDF.zeitstempel[kauf]),  # X-Werte, Zeitstempel der Daten wenn TransaktionsTyp = Kauf
                    # Für die Y-Werte wird der Kaufpreis der Aktie berechnet. Also die Menge an ausgegebenem Kapital durch die Anzahl der gekauften Aktien
                    (-1)*(kaufVerkaufDF.kapital_bestand_aenderung[kauf] / kaufVerkaufDF.stueck_bestand_aenderung[kauf]), 
                    size=20, color="blue", alpha=0.5, legend_label="Käufe"
                )
                plot.circle( # Punkte für Verkäufe
                    pd.to_datetime(kaufVerkaufDF.zeitstempel[verkauf]), # X-Werte Zeitstempel der Daten wenn TransaktionsTyp = Verkauf
                    # Für die Y-Werte wird der Verkaufspreis der Aktie berechnet. Also die Menge an erhaltenem Kapital durch die Anzahl der verkauften Aktien
                    (-1)*(kaufVerkaufDF.kapital_bestand_aenderung[verkauf] /kaufVerkaufDF.stueck_bestand_aenderung[verkauf]), 
                    size=20, color="yellow", alpha=0.5, legend_label="Verkäufe"
                )

        # Hier werden alle Legenden Einstellungen und allg. Koordinaten System Einstellungen gemacht
        for plot in plotListe:
            plot.legend.location = "top_left"
            plot.legend.title = 'Graphen'
            plot.legend.title_text_font_style = "bold"
            plot.legend.title_text_font_size = "20px"
            plot.legend.click_policy = "hide"

            plot.output_backend = "svg"
            plot.background_fill_color = "#f5f5f5"
            plot.grid.grid_line_color = "white"
            plot.axis.axis_line_color = None
            plot.xaxis.major_label_orientation = pi/4
        

        # script, div = components(Tabs(tabs=[tab1, tab2]))
        script, div = components(column(plotListe))

        return render(request, 'simulation/simulation_ergebnis.html', {'script': script, 'div': div, 'daten': anzeigeDaten})

def pruefeObEigeneSkala(ID,callerSelf):
    """
        Funktion zum Prüfen ob ein Indikator mit der angegebenen ID eine eigene Skala hat. 
        Hierbei werden die Indikatordaten geholt und, wenn kein Fehler aufgetreten ist, der Wert für eigene_skala zurückgegeben
        """
    serverAntwort = datenAnBackendSenden(
            hauptPfad = "indikator/", 
            unterPfad = "get", 
            daten     = {
                "id"          : int(ID),
                "benutzer_id" : callerSelf.request.user.username,
            }
    )

    if(allgemeineFehlerPruefung(serverAntwort, callerSelf.request)):
            return redirect(reverse('simulation:simulation-fehler'))  

    return serverAntwort["indikator"]["eigene_skala"]
    
def downloadCSV(request):
    """
    Funktion für das Generieren eines CSV mit allen Simulationsergebnis-Daten.
    Dabei werden alle Daten für eine deutsche Ansicht umgewandelt, 
    d.h. Punkte bei Zahlenwerten werden zu Kommas und Zeitstempel werden in ein akzeptiertes Format umgewandelt
    """

    daten = request.session["simulationsDaten"] # Daten aus der Session holen
    datumUhrzeit = datetime.now().strftime('--%d-%m-%Y--%H-%M-%S') # aktueller Zeitstempel für Datei Namensgebung
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="'+daten["strategie"]["name"]+datumUhrzeit+'.csv"' # Festlegung des Datei-Namens
    writer = csv.writer(response, delimiter=';')
    
    
    # Die Gewählte ISIN, die Bezeichnung des wertpapiers und der eingestellte Testzeitraum in einzelne Zeilen schreiben    
    writer.writerow(["ISIN", daten["wertpapier"]["isin"]])
    writer.writerow(["Bezeichnung", daten["wertpapier"]["name"]])
    writer.writerow(["Start Datum", daten["start_datum"]])
    writer.writerow(["End Datum", daten["end_datum"]])

    # Hier werden alle einzelnen Strategie Attribute in einzelne Zeilen mit entsprechender Bezeichnung geschrieben.
    writer.writerow(["Strategie Daten"])
    for strategieAttribut in daten["strategie"]: # 
        writer.writerow(
            ["", strategieAttribut, daten["strategie"][strategieAttribut]])

    # Hier werden alle einzelnen Strategie Statistik Daten in einzelne Zeilen mit entsprechender Bezeichnung geschrieben.
    writer.writerow(["Strategie Statistik Daten"])
    for strategieStatistikWert in daten["strategie_statistik"]:
        writer.writerow(["", strategieStatistikWert,
                         daten["strategie_statistik"][strategieStatistikWert]])

    leerzeichenListe = [1, 5, 2, 4] # Wie viele Leere Spalten zwischen den einzelnen Spalten sein sollen, dabei wird angefangen mit den leeren Spalten
    spaltenNamenListe = ["Kurs Zeitreihe", "Strategie Kurs Zeitreihe",
                         "Kaeufe/Verkaeufe Zeitreihe", "Indikator Zeitreihe(n)"]
    spaltenNamenZeile = []

    # Für jeden Spaltennamen
    for idx, spaltenName in enumerate(spaltenNamenListe):
        
        for i in range(leerzeichenListe[idx]): # wird die Anzahl der vorlaufenden Leerzeichen entsprechend der leerzeichenListe der spaltenNamenZeile angefügt
            spaltenNamenZeile.append("")
        # dann der Spaltennamen wert angehängt
        spaltenNamenZeile.append(spaltenName)
    # spaltenNamenZeile wird als eine Zeile in die CSV geschrieben
    writer.writerow(spaltenNamenZeile)

    

    
    # Danach kommen der Bereich mit den Kursdaten also close, high, low, open und volumen. Zusätzlich wird hier der zeitstempel mit aufgelistet
    # Dann der Bereich mit den Strategiekursdaten also kurs_kapital und kurs_prozentual
    # Dann kommt der Bereich mit den  Kauf/Verkauf daten also regel, typ, stueck_bestand_aenderung und kapital_bestand_aenderung
    kursDatenBereich          = ["zeitstempel", "close", "high", "low", "open", "volumen"]
    strategiekursdatenBereich = ["kurs_prozentual", "kurs_kapital"]
    kaufVerkaufDatenBereich   = ["regel", "typ", "stueck_bestand_aenderung", "kapital_bestand_aenderung"]

    alleBereiche = [kursDatenBereich,strategiekursdatenBereich,kaufVerkaufDatenBereich]

    spaltenNamenListe = []
    spaltenNamenListe.extend(kursDatenBereich) 
    spaltenNamenListe.extend(strategiekursdatenBereich)
    spaltenNamenListe.extend(kaufVerkaufDatenBereich)

    bereichBreiten = [] # Liste mit den Breiten der einzelnen Bereiche
    for bereich in alleBereiche: # Die Breite von jedem Bereich in die bereichBreiten Liste hinzufügen
        bereichBreiten.append(len(bereich))

    indikatorBereichBreite = 0
    # Die Bereich mit den einzelnen Indikatoren wird dynamisch wie folgt generiert:
    # für jeden key != zeitstempel, also jeden Indikator
    for key in daten["indikator_zeitreihe"][0]:
        if(key != "zeitstempel"):
            # wird jeder graph des Indikators mit entsprechendem Namen zur spaltenNamenListe angefügt
            for graph in daten["indikator_zeitreihe"][0][key]:
                spaltenNamenListe.append("Indikator " + key + " - " + graph)
                # und die breite des Indikatorbereichs um eins erhöht.
                indikatorBereichBreite += 1
    bereichBreiten.append(indikatorBereichBreite) # Der entgültige Wert wird zur bereichBreiten-liste hinzugefügt
    
    spaltenNamenZeile = []  
    counter = 0
    # Hier werden die einzelnen Spaltennamen zur spaltenNamenZeile Liste angefügt 
    # Abhängig von der bereichBreite, werden entsprechend viele Bezeichnungen zur spaltenNamenZeile hinzugefügt. Nach jedem Bereich kommt eine leere Spalte
    print(bereichBreiten)
    for breite in bereichBreiten:
        for i in range(breite):
            print(spaltenNamenListe[counter])
            spaltenNamenZeile.append(spaltenNamenListe[counter])
            counter += 1
        spaltenNamenZeile.append("") # Leere Spalte zwischen Bereichen
    writer.writerow(spaltenNamenZeile)

    kaufVerkaufCounter = 0 # Für das Zählen von bereits aufgeschriebenen Käufen/Verkäufen
    for idx, datensatz in enumerate(daten["indikator_zeitreihe"]): # für jeden Datensatz in den indikator-zeitreihe
        einzelneZeile = [] # Neue Zeile initialisieren
        einzelneZeile.append(datetime.strptime(datensatz["zeitstempel"],'%Y-%m-%dT%H:%M:%S%z').strftime('%d.%m.%Y %H:%M:%S')) # Zeitstempel anfügen

        # für jeden einzelne Wert in der kurs_zeitreihe außer zeitstempel
        for wert in daten["kurs_zeitreihe"][0]: # wert ist hierbei der key 
            if(wert != "zeitstempel"):
                # Werte an Zeile anfügen, Punkt mit Komma ersetzen für deutsche Darstellung
                einzelneZeile.append(str(daten["kurs_zeitreihe"][idx][wert]).replace(".",",")) 

        # für jeden einzelne Wert in der strategie_kurs_zeitreihe außer zeitstempel
        for element in daten["strategie_kurs_zeitreihe"][0]:
            if(element != "zeitstempel"):
                # Werte an Zeile anfügen, Punkt mit Komma ersetzen für deutsche Darstellung
                einzelneZeile.append(str(daten["strategie_kurs_zeitreihe"][idx][element]).replace(".",",")) 
                
        einzelneZeile.append("") #Spalte zwischen Bereichen

        # Prüfen ob strategie_kaeufe_verkaeufe_zeitreihe Werte enthält
        if(len(daten["strategie_kaeufe_verkaeufe_zeitreihe"]) != 0):
            # Prüfen ob der kaufVerkaufCounter kleiner als die Anzahl der kaufVerkauf-Daten in strategie_kaeufe_verkaeufe_zeitreihe
            if(kaufVerkaufCounter < len(daten["strategie_kaeufe_verkaeufe_zeitreihe"])): 
                # prüfen ob für den aktuellen zeitstempel ein Kauf/verkauf getätig wurde
                if(datensatz["zeitstempel"] == daten["strategie_kaeufe_verkaeufe_zeitreihe"][kaufVerkaufCounter]["zeitstempel"]):
                    # wenn Kauf/Verkauf getätigt wurde dann die einzelnen Werte an die Zeile hängen
                    for wert in daten["strategie_kaeufe_verkaeufe_zeitreihe"][0]:
                        if(wert != "zeitstempel"):
                            einzelneZeile.append(
                                str(daten["strategie_kaeufe_verkaeufe_zeitreihe"][kaufVerkaufCounter][wert]).replace(".",","))

                    kaufVerkaufCounter += 1  # Anzahl der bereits aufgeschriebenen Käufen/Verkäufen um eins erhöhen
                else:
                    # Wenn kein Kauf/Verkauf getätigt wurde, jeden Wert eine leere Spalte anhängen um Format beizubehalten
                    for element in daten["strategie_kaeufe_verkaeufe_zeitreihe"][0]:
                        if(element != "zeitstempel"):
                            einzelneZeile.append("")
            else:
                # Wenn kaufVerkaufCounter >= als die Anzahl der kaufVerkauf-Daten in strategie_kaeufe_verkaeufe_zeitreihe
                # Alle Käufe/Verkäufe wurden bereits aufgeschrieben, also leere Spalte anhängen um Format beizubehalten
                for element in daten["strategie_kaeufe_verkaeufe_zeitreihe"][0]:
                    if(element != "zeitstempel"):
                        einzelneZeile.append("")
        else:
            # Wenn keine Kauf/Verkauf Daten vorhanden, leere Spalte anhängen um Format beizubehalten
            einzelneZeile.append("")
            einzelneZeile.append("")
            einzelneZeile.append("")
            einzelneZeile.append("")

        einzelneZeile.append("") #Spalte zwischen Bereichen

        # Für jedes Element in der indikator_zeitreihe ungleich dem zeitstempel, also für jeden Indikator
        for element in daten["indikator_zeitreihe"][0]:
            if(element != "zeitstempel"):
                # Für jeden einzelnen Graphen des Indikators
                for graph in daten["indikator_zeitreihe"][idx][element]:
                    # Den Wert des jeweiligen Graphen an die Zeile hängen, Punkt mit Komma ersetzen für deutsche Darstellung
                    einzelneZeile.append(
                        str(daten["indikator_zeitreihe"][idx][element][graph]).replace(".",","))
                    
        
        # die Zeile in CSV schreiben
        writer.writerow(einzelneZeile) 

    return response