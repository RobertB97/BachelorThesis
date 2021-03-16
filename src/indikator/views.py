# imports die bei der Graphenerstellung benötigt werden
import itertools
import json
import pandas as pd
import requests

from datetime import datetime
from math     import pi

from bokeh.embed    import components
from bokeh.layouts  import column
from bokeh.models   import Panel, Tabs
from bokeh.palettes import Dark2_5 as palette
from bokeh.plotting import figure

from django.conf      import settings
from django.shortcuts import redirect, render, reverse
from django.views     import View
# -------------

#mixins
from trading.mixins import (
    hinzufuegenViewMixin,
    listenViewMixin,
    detailViewMixin,
    bearbeitenViewMixin,
    entfernenViewMixin,
    fehlerViewMixin,

    datenAnBackendSenden,
    allgemeineFehlerPruefung
)

# Indikator app imports
from .forms  import IndikatorModelForm
from .models import Indikator

appName = "indikator"

class IndikatorListeView(listenViewMixin):
    """
        Klasse der Ansicht für das Darstellen der Indikatoren in einer Liste.
        """  
         
    appName             = appName

class IndikatorHinzufuegenView(hinzufuegenViewMixin):  
    """
        Klasse der Ansicht für das Erstellen/ Hinzufügen von neuen Indikatoren.
        """   
    
    form_class    = IndikatorModelForm
    appName       = appName
    model         = Indikator

    neuErstellen  = True
                        
class IndikatorDetailView(detailViewMixin):
    """
        Klasse der Ansicht für das Darstellen eines einzelnen Indikators.
        """  
    
    template_name = 'modulViews/generisch_detail.html' 
    appName       = appName
    model         = Indikator 

class IndikatorBearbeitenView(bearbeitenViewMixin):
    """
        Klasse der Ansicht für das Bearbeiten eines existierenden Indikators.
        """  

    template_name = 'modulViews/generisch_bearbeiten.html'  
    form_class    = IndikatorModelForm
    appName       = appName
    model         = Indikator 

class IndikatorEntfernenView(entfernenViewMixin):
    """
        Klasse der Ansicht für das Löschen eines Indikators.
        """  

    template_name = 'modulViews/generisch_entfernen.html' 
    appName       = appName
    model         = Indikator
    
class IndikatorFehlerView(fehlerViewMixin):
    """
        Klasse der Ansicht für das Anzeigen von jeglichen Fehlermeldungen.
        """  

    appName       = appName

class IndikatorGraphView(View):
    """
        Klasse der Ansicht für das Anzeigen der Indikator-Graph-Ansicht.

        Methoden
        ------
        get
            Holt die benötigten Daten und generiert daraus Graphen. 
        """
    template_name = 'indikator/indikator_graph.html'

    def get(self, request, *args, **kwargs):
        """
            Hier werden die benötigten Indikator- und Kursdaten geholt und in die entsprechenden Graphiken eingefügt.

            Es werden mit der Bibliothek "bokeh" für die Kursdaten als Referenzwert und die Daten des Indikators die entsprechenden Graphen generiert.
            Es werden insgesamt 2 Koordinaten-Systeme generiert.
            Im ersten sind die Aktienkurse-Daten des DAX als Candles dargestellt sowie alle Graphen des ausgewählten Indikators.
            Im zweiten sind die Aktienkurse-Daten des DAX als Linie dargestellt sowie alle Graphen des ausgewählten Indikators.
            Bei beiden Koordinaten-Systemen wird der Zeitraum vom 01.0.1.2019 bis 31.12.2020 dargestellt.
        """
        daten   = {
            "id"          : self.kwargs.get("id"),
            "benutzer_id" : self.request.user.username,
            "isin"        : "DE0008469008", 
            "start_datum" : "2019-01-01",
            "end_datum"   : "2020-12-31"
        }
    
        # Kurs daten werden hier geholt --------------
        aktienkursDaten = datenAnBackendSenden(
            hauptPfad = "kurs",
            unterPfad = "/get",
            daten     = daten
        )

        # Prüfen ob kein Fehler entstanden ist
        # Wenn ja auf FehlerSeite leiten
        if(allgemeineFehlerPruefung(serverAntwort = aktienkursDaten, request = request)):
            return redirect(reverse('indikator:indikator-fehler')) 
        # -----------------------
        
        # Indikatorgraph-Daten werden hier geholt, angewandt auf der oben festgelegten ISIN
        serverAntwort = datenAnBackendSenden(
            hauptPfad = "indikator",
            unterPfad = "/auswerten",
            daten     = daten
        )
        # Prüfen ob kein Fehler entstanden ist
        # Wenn ja auf FehlerSeite leiten
        if(allgemeineFehlerPruefung(serverAntwort = serverAntwort, request = request)):
            return redirect(reverse('indikator:indikator-fehler'))      
        # -----------------------

        indikatorenDaten = serverAntwort["indikator_zeitreihe"] # Die Indikatordaten werden für eine einfachere Verarbeitung in ein eigenes Objekt kopiert.
        keyListe         = indikatorenDaten[0].keys()
        listenDict       = {}

        # ersetze alle Leerzeichen mit der Leerzeichen Entity 
        serverAntwort["indikator"]["berechnung_pseudo_code"] = serverAntwort["indikator"]["berechnung_pseudo_code"].replace(" ","&nbsp")
        # ersetze vier aufeinander folgende Leerzeichen durch zu 4 Leerzeichen Entity 
        serverAntwort["indikator"]["berechnung_pseudo_code"] = serverAntwort["indikator"]["berechnung_pseudo_code"].replace("	","&nbsp&nbsp&nbsp&nbsp")
        
        # Für jeden key wird eine Leere Liste im listenDict angelegt
        for key in keyListe:
            listenDict[key] = []

        # Jeder Datensatz in den IndikatorDaten wird an die entsprechende Liste im ListenDict Dictionary angehängt
        for datensatz in indikatorenDaten:
            for key in keyListe:
                listenDict[key].append(datensatz[key])

        p1 = figure( # Koordinaten-System Deklaration
            plot_width  = 1000, 
            plot_height = 700,
            x_axis_type = "datetime", 
            tools       = "pan,wheel_zoom,box_zoom,reset,save") 
        p2 = figure( # Koordinaten-System Deklaration
            plot_width  = 1000, 
            plot_height = 700,
            x_axis_type = "datetime", 
            tools       = "pan,wheel_zoom,box_zoom,reset,save",
            x_range     = p1.x_range, 
            y_range     = p1.y_range)

        plotListe = [p1,p2]
        # Wandelt die zeitstempel Daten in ein DataFrame um
        zeitstempelDataFrame                = pd.DataFrame(listenDict["zeitstempel"], columns = ['zeitstempel'])
        # Die Daten in der Spalte "zeitstempel" müssen in das entsprechende Format umgewandelt werden
        zeitstempelDataFrame["zeitstempel"] = pd.to_datetime(zeitstempelDataFrame["zeitstempel"]) 
        
        #Wandelt die kurs_zeitreihe Daten in ein DataFrame um
        aktienKursDataFrame                 = pd.DataFrame(aktienkursDaten["kurs_zeitreihe"])
        # Die Daten in der Spalte "zeitstempel" müssen in das entsprechende Format umgewandelt werden
        aktienKursDataFrame["zeitstempel"]  = pd.to_datetime(aktienKursDataFrame["zeitstempel"])
        
        # Boolean der prüft, ob aktienKursDataFrame.close größer aktienKursDataFrame.open 
        inc = aktienKursDataFrame.close > aktienKursDataFrame.open 
        # Boolean der prüft, ob aktienKursDataFrame.close kleiner aktienKursDataFrame.open 
        dec = aktienKursDataFrame.close < aktienKursDataFrame.open
        kerzenBreite = 12 * 60 * 60 * 1000 # halber Tag in ms, für die Breite der Kerzen

        #Jeder "Punkt" eines segment ist eine Linie die aus zwei Koordinaten-Paaren besteht. 
        p1.segment(  # Hier werden die High und Lows für jeden Tag erstellt
            aktienKursDataFrame.zeitstempel, # Paar-1 Werte für x-Achse 
            aktienKursDataFrame.high, # Paar-1 Werte für y-Achse 
            aktienKursDataFrame.zeitstempel, # Paar-2 Werte für x-Achse 
            aktienKursDataFrame.low, # Paar-2 Werte für y-Achse 
            color = "black",
            legend_label = "High-Low-Linien"
        )
        # Jedes "Punkt" einer vbar ist ein Rechteck mit einem x-Wert, einer Breite, und zwei Werten für die y-Achse (Rechteck-Höhe)
        p1.vbar( # Hier werden die grünen Kerzen "Torsos" erstellt
            aktienKursDataFrame.zeitstempel[inc], # Werte für x-Achse 
            kerzenBreite, 
            aktienKursDataFrame.open[inc],  # Teil 1 Werte für y-Achse
            aktienKursDataFrame.close[inc], # Teil 2 Werte für y-Achse
            fill_color = "green", 
            line_color = "black",
            legend_label = "Grüne Candlesticks"
        )

        p1.vbar( # Hier werden die roten Kerzen "Torsos" erstellt
            aktienKursDataFrame.zeitstempel[dec], # Werte für x-Achse 
            kerzenBreite, 
            aktienKursDataFrame.open[dec],  # Teil 1 Werte für y-Achse
            aktienKursDataFrame.close[dec], # Teil 2 Werte für y-Achse
            fill_color = "red", 
            line_color = "black",
            legend_label = "Rote Candlesticks",
        )  

        #Jeder Punkt einer line braucht ein Koordinaten-Paar
        p2.line( # Hier wird der Aktienkurs als Linie erstellt
            aktienKursDataFrame.zeitstempel, # Werte für x-Achse 
            aktienKursDataFrame.close,       # Werte für y-Achse 
            line_width    = 3, 
            color        = "red", 
            alpha        = 0.5, 
            legend_label = "DAX"
        )   

        farben = itertools.cycle(palette) # Farbenauswahl
        
        for key in keyListe:
            if(key != "zeitstempel"):
                # Jede einzelne Liste im ListenDict wird in ein DataFrame umgewandelt, außer die Liste mit dem key "zeitstempel"
                elementDataFrame = pd.DataFrame(listenDict[key])
                for graph in listenDict[key][0].keys():
                   
                    # für eine korrekte Darstellung müssen alle Graphen das selbe Zeitstempel DataFrame verwenden
                    # hier werden die Graphen-Werte der einzelnen Graphen mit den Zeitstempeln des zeitstempelDataFrame zu einen einzigen DataFrame vereinigt
                    angepassteDatenPunkte = pd.concat(
                        [zeitstempelDataFrame,elementDataFrame[graph]],axis=1
                    )
                    farbe = next(farben)
                    # und in beide Koordinatensysteme eingefügt
                    if(serverAntwort["indikator"]["eigene_skala"]):
                        p3 = figure( # Koordinaten-System Deklaration
                            plot_width  = 1000, 
                            plot_height = 700,
                            x_axis_type = "datetime", 
                            tools       = "pan,wheel_zoom,box_zoom,reset,save",
                            x_range     = p1.x_range)
                        p3.line( # 
                            zeitstempelDataFrame["zeitstempel"], 
                            angepassteDatenPunkte[graph], 
                            line_width   = 3, 
                            color        = farbe, 
                            alpha        = 1,
                            legend_label = "ID " + key + " - " + graph,
                        )
                        plotListe.append(p3)
                        
                    else:
                        for plot in plotListe:
                            plot.line(
                                zeitstempelDataFrame["zeitstempel"], 
                                angepassteDatenPunkte[graph], 
                                line_width   = 3, 
                                color        = farbe, 
                                alpha        = 1,
                                legend_label = "ID " + key + " - " + graph,
                            )
                        

        
        # An beide Koordinaten-Systeme werden die gleichen Legenden Einstellungen sowie Stylingattribute vergeben
        for plot in plotListe:
            #Legenden Einstellung
            plot.legend.location               = "top_left"
            plot.legend.title                  = 'Graphen'
            plot.legend.title_text_font_style  = "bold"
            plot.legend.title_text_font_size   = "20px"
            plot.legend.click_policy           = "hide"
            #Koordinaten-System Styling
            plot.background_fill_color         = "#f5f5f5"
            plot.grid.grid_line_color          = "white"
            plot.axis.axis_line_color          = None
            plot.xaxis.major_label_orientation = pi/4


        tab1        = Panel(child = p1, title = "Candlesticks")
        tab2        = Panel(child = p2, title = "Linie")
        if(len(plotListe) == 2):
            script, div = components(Tabs(tabs = [tab1, tab2]))
        else:
            script, div = components(column(Tabs(tabs = [tab1, tab2]),p3))
        return render(
            request, 'indikator/indikator_graph.html', 
            {'script': script, 'div': div,'daten': serverAntwort["indikator"],'bearbeitbar' : self.request.session["bearbeitbar"]}
        )
