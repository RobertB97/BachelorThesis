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
from bokeh.models import HoverTool, Panel, Tabs
from bokeh.palettes import Spectral4
from bokeh.plotting import figure, output_file, show
from bokeh.sampledata.stocks import AAPL, GOOG, IBM, MSFT

from datetime import datetime

from math import pi 

import pandas as pd

import numpy as np

fehler_message = "Hoppla, da ist wohl etwas schiefgelaufen"

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

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w

class IndikatorHinzufuegenView(CreateView):   
    template_name = 'indikator/indikator_hinzufuegen.html'
    form_class = IndikatorModelForm
    success_url = '/indikatoren/' 
    #queryset = Indikator.objects.all() # ohne api
    

    
    def form_valid(self, form):
        
        form.cleaned_data['nutzername'] = self.request.user.username
        #IN CASE THE INPUT NEEDS TO BE CLEANED UP
        # codeFeldEingabe  = form.cleaned_data["code"]
        # start = codeFeldEingabe.find('<code class="language-python">') + len('<code class="language-python">')
        # end = codeFeldEingabe.find("</code>")
        # reinerCode = codeFeldEingabe[start:end]
        # form.cleaned_data["code"] = reinerCode
        
        temp = versuche_request(self,form,"POST",None)
        print(temp)
        if(temp==500):
            return HttpResponse(fehler_message)
        if(temp==200):
            return super().form_valid(form) 

        
class IndikatorListeView(ListView):
    template_name = 'indikator/indikator_liste.html'
    
    def get_queryset(self):
        temp = versuche_request(self, None,"GET",None)
        if(temp==500):
            return {}
        return temp

class IndikatorDetailView(DetailView):
    template_name = 'indikator/indikator_detail.html' 

    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        return temp

class IndikatorBearbeitenView(UpdateView):
    template_name = 'indikator/indikator_bearbeiten.html'  
    form_class = IndikatorModelForm
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def form_valid(self, form):
        id_ = self.kwargs.get("id")
        form.cleaned_data['nutzername'] = self.request.user.username
        temp = versuche_request(self,form,"PUT",id_)
        if(temp==500):
            return HttpResponse(fehler_message)    
        if(temp==200):
            return super().form_valid(form) 

class IndikatorEntfernenView(DeleteView):
    template_name = 'indikator/indikator_entfernen.html' 
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def get_success_url(self):
        return reverse('indikator:indikator-liste')

def versuche_request(outerself, form, http_methode, id):
    url = 'http://localhost:8001/indikatoren/'
    if(id != None):
        url = url + str(id)+"/"
    if(form!=None):
        daten=form.cleaned_data
    try:
        if(http_methode=="GET"):
            queryset = requests.get(url)
            if(id == None):
                queryset = queryset.json()
                return queryset
        if(http_methode=="POST"):
            queryset = requests.post(url, data=daten)
        if(http_methode=="PUT"):
            queryset = requests.put(url, data=daten)
            print(queryset)
        
    except ConnectionError as e:
        return 500
    if(id !=None and http_methode=="GET"):
        jsonObjekt = json.loads(queryset.text)
        objektFuerDarstellung = Indikator()
        for key in jsonObjekt.keys(): 
            if key in dir(objektFuerDarstellung):
                setattr(objektFuerDarstellung,key,jsonObjekt[key])
        return objektFuerDarstellung
    return 200