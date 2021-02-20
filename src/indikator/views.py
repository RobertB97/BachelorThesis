from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView,
    TemplateView
)
from .forms import IndikatorModelForm
from .models import Indikator
import requests
from requests.exceptions import ConnectionError
from django.http import HttpResponse, JsonResponse
import json

from bokeh.embed import components
from bokeh.models import HoverTool, Panel, Tabs, ColumnDataSource
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, output_file, show
from bokeh.sampledata.stocks import AAPL, GOOG, IBM, MSFT
from django.conf import settings
from datetime import datetime

from math import pi 

import pandas as pd

import numpy as np

fehler_message = "Hoppla, da ist wohl etwas schiefgelaufen"
mainUrl = "http://f4478b09b5e6.eu.ngrok.io/"
mainPath = "indikator/"

class IndikatorGraphView(View):
    template_name = 'indikator/indikator_graph.html'



    def get(self,request,*args,**kwargs):
        id_ = self.kwargs.get("id")
        daten = versuche_request(self,None,"GET",id_)

        
        df = pd.DataFrame(MSFT)[:200]
        df["date"] = pd.to_datetime(df["date"])

        inc = df.close > df.open # inc ist ein boolean, welcher True zurückgibt wenn Close > Open
        
        dec = df.open > df.close # dec ist ein boolean, welcher True zurückgibt wenn Open > Close
        w = 12*60*60*1000 # halber Tag in ms, für die Breite der Kerzen
        print(df)
        TOOLTIPS = [
            ("date", "@timestamp{%H:%M}"),
            ("open", )
        ]

        
        p1 = figure(plot_width=800, plot_height=500)
        # map dataframe indices to date strings and use as label overrides
        p1.xaxis.major_label_overrides = {
            i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df["date"]))
        }

        test = moving_average(df.close,14)

        # use the *indices* for x-axis coordinates, overrides will print better labels
        p1.segment(df.index, df.high, df.index, df.low, color="black",legend_label="HighLows")  # Hier werden die High und Lows für jeden Tag erstellt
        p1.vbar(df.index[inc], 0.5, df.open[inc], df.close[inc], fill_color="green", line_color="black", legend_label="Grüne Kerzen")# Hier werden die grünen Kerzen "Torsos" erstellt
        p1.vbar(df.index[dec], 0.5, df.open[dec], df.close[dec], fill_color="red", line_color="black",legend_label="Rote Kerzen")# Hier werden die roten Kerzen "Torsos" erstellt
        p1.line(df.index, test, line_width=3, color="navy", alpha=0.5,legend_label="Moving Average")

        p1.legend.location = "top_left"
        p1.legend.title = 'Stock'
        p1.legend.title_text_font_style = "bold"
        p1.legend.title_text_font_size = "20px"
        p1.legend.click_policy="hide"


        tab1 = Panel(child=p1, title="Candlesticks")

        
        p2 = figure(plot_width=800, plot_height=500, x_range=p1.x_range, y_range=p1.y_range)

        p2.xaxis.major_label_overrides = {
            i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df["date"]))
        } 
        p2.line(df.index, df.close, line_width=3, color="red", alpha=0.5, legend_label="Stock price")
        p2.line(df.index, test, line_width=3, color="navy", alpha=0.5,legend_label="Moving Average")

        p2.legend.location = "top_left"
        p2.legend.title = 'Stock'
        p2.legend.title_text_font_style = "bold"
        p2.legend.title_text_font_size = "20px"
        p2.legend.click_policy="hide"
        tab2 = Panel(child=p2, title="Linie")

        

        script, div = components(Tabs(tabs=[tab1, tab2])  )
        return render(request, 'indikator/indikator_graph.html', {'script':script, 'div':div,'daten':daten})
        # id_ = self.kwargs.get("id")
        # daten = versuche_request(self,None,"GET",id_)
        # df = pd.DataFrame(MSFT)[:200]
        # df["date"] = pd.to_datetime(df["date"])

        
        # w = 12*60*60*1000 # half day in ms
        # """
        # main
        # 0 = date
        # 1 = open
        # 2 = high
        # 3 = low
        # 4 = close
        # 5 = volume
        # 6 = ajd_close
        # """

        # # main=[]
        # # lol = df.columns.values.tolist()
        # # counterOne = 0
        # # for i in lol:
        # #     counterTwo = df[i].size -1
        # #     list = []
        # #     while(counterTwo>=0):
        # #         list.append(df[i][counterTwo])
        # #         counterTwo = counterTwo - 1
        # #     main.append(list)

        
        # # dateList = main[0]
        # # openList = main[1]
        # # highList = main[2]
        # # lowList = main[3]
        # # closeList = main[4]
        # # volumeList = main[5]
   
        # hover = HoverTool(
        #     tooltips=[
        #         ('datum', '@timestamp{%F}'),
        #         ('open', '@open{0}'),
        #         ('high', '@high{0}'),
        #         ('low', '@low{0}'),
        #         ('close', '@close{0}'),
        #         ('volume', '@volume{0}'),
        #     ],

        #     formatters={
        #         '@timestamp': 'datetime'
        #     },
        #     mode='mouse'
        # )
        
        # inc = df.close > df.open
        # dec = df.open > df.close

        # sourceInc = ColumnDataSource(data=dict(timestamp=df.date[inc], open=df.open[inc], close=df.close[inc]))
        # sourceDec = ColumnDataSource(data=dict(timestamp=df.date[dec], open=df.open[dec], close=df.close[dec]))

        # mainSource = ColumnDataSource(data=dict(timestamp=df.date,high=df.high,low=df.low))


        # p1 = figure(x_axis_type="datetime",plot_width=800, plot_height=500)
        # p1.xaxis.major_label_overrides = {
        #     i: date.strftime('%b %d') for i, date in enumerate(pd.to_datetime(df["date"]))
        # }
        # # map dataframe indices to date strings and use as label overrides
        # p1.segment(source=mainSource, x0='timestamp', x1='timestamp', y0='high', y1='low', color="black")
        # p1.vbar(source=sourceInc,  x='timestamp', width=w, top='open', bottom='close', fill_color="green", line_color="green")
        # p1.vbar(source=sourceDec,  x='timestamp', width=w, top='open', bottom='close', fill_color="red", line_color="red")
        # p1.add_tools(hover)

        

        # p1.legend.location = "top_left"
        # p1.legend.title = 'Stock'
        # p1.legend.title_text_font_style = "bold"
        # p1.legend.title_text_font_size = "20px"
        # p1.legend.click_policy="hide"





        # script, div = components(p1)
        # return render(request, 'indikator/indikator_graph.html', {'script':script, 'div':div,'daten':daten})

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

class IndikatorHinzufuegenView(CreateView):   
    template_name = 'indikator/indikator_hinzufuegen.html'
    form_class = IndikatorModelForm
    success_url = '/indikatoren/' 
    #queryset = Indikator.objects.all() # ohne api
    

    
    def form_valid(self, form):
        subPath = "hinzufuegen"
        #IN CASE THE INPUT NEEDS TO BE CLEANED UP
        # codeFeldEingabe  = form.cleaned_data["code"]
        # start = codeFeldEingabe.find('<code class="language-python">') + len('<code class="language-python">')
        # end = codeFeldEingabe.find("</code>")
        # reinerCode = codeFeldEingabe[start:end]
        # form.cleaned_data["code"] = reinerCode
        
        daten = {
            "benutzer_id": self.request.user.username,
            "name": form.cleaned_data["name"],
            "beschreibung": form.cleaned_data["beschreibung"],
            "berechnung_pseudo_code": form.cleaned_data["code"],
        }
        antwort = versuche_request(subPath,daten)
        if(antwort == "ConnectionError"):
            return HttpResponse(fehler_message)
        else:
            if("Fehler" in antwort):
                return HttpResponse(antwort["Fehler"]) #TODO popup instead
            else:
                return super().form_valid(form) 
            

        
class IndikatorListeView(ListView):
    template_name = 'indikator/indikator_liste.html'
    
    def get_queryset(self):
        subPath = "getalle"
        daten = {
            "benutzer_id": self.request.user.username,
        }
        antwort = versuchePost(subPath,daten)
        #{"Fehler": "Keine Objekte vorhanden [mysql_tabelle: indikatoren]"} 
        if(antwort == "ConnectionError"):
            return HttpResponse(fehler_message)
        else:
            if("Fehler" in antwort):
                return HttpResponse(antwort["Fehler"]) #TODO popup instead
            else:
                return antwort["indikatoren"]

class IndikatorDetailView(DetailView):
    template_name = 'indikator/indikator_detail.html' 

    def get_object(self):
        return holeObjekt(self)

        #{"Fehler": "Objekt nicht gefunden [id: 14, benutzer_id: admin, mysql_tabelle: indikatoren]"}
            
class IndikatorBearbeitenView(UpdateView):
    template_name = 'indikator/indikator_bearbeiten.html'  
    form_class = IndikatorModelForm
    
    def get_object(self):
        return holeObjekt(self)


    def form_valid(self, form):
        id_ = self.kwargs.get("id")

        daten = {
            "id": self.kwargs.get("id"),
            "benutzer_id": self.request.user.username,
            "name": form.cleaned_data["name"],
            "beschreibung": form.cleaned_data["beschreibung"],
            "berechnung_pseudo_code": form.cleaned_data["code"],
        }
        
        antwort = versuchePost(subPath,daten)
        if(antwort == "ConnectionError"):
            return HttpResponse(fehler_message)
        else:
            if("Fehler" in antwort):
                return HttpResponse(antwort["Fehler"]) #TODO popup instead
            else:   
                return super().form_valid(form) 

class IndikatorEntfernenView(DeleteView):
    template_name = 'indikator/indikator_entfernen.html' 
    
    def get_object(self):
        return holeObjekt(self)

    def get_success_url(self):
        return reverse('indikator:indikator-liste')

def versuchePost(subPath,daten):
    url = settings.BACKEND_URL + mainPath + subPath
    try:
        queryset = requests.post(url, json=daten)
        print(queryset) #TODO remove when done
        #{"indikator": {"id": 13, "benutzer_id": "superuser", "name": "Test", "beschreibung": "Test", "erstell_datum": "2021-02-20T13:56:21", "aenderungs_datum": "2021-02-20T13:56:21", "berechnung_pseudo_code": "~Ausgabe(sma_20)~ = numpy.mean(~Kurs(close,-20,0,i)~)", "verwendete_indikatoren": []}}
    except ConnectionError as e:
        return "ConnectionError" # TODO Popup
    return queryset.text

def holeObjekt(outerself)
    subPath = "get"
    daten = {
        "id": outerself.kwargs.get("id"),
        "benutzer_id": outerself.request.user.username,
    }
    antwort = versuchePost(subPath,daten)
    if(antwort == "ConnectionError"):
        return HttpResponse(fehler_message)
    else:
        if("Fehler" in antwort):
            return HttpResponse(antwort["Fehler"]) #TODO popup instead
        else:
            objektFuerDarstellung = Indikator()
            for key in antwort.keys(): 
                if key in dir(objektFuerDarstellung):
                    setattr(objektFuerDarstellung,key,antwort[key])
            return objektFuerDarstellung