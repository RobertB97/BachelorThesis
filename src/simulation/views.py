
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView
)

from bokeh.embed import components
from bokeh.models import HoverTool
from bokeh.plotting import figure, output_file, show
from bokeh.sampledata.stocks import MSFT

from datetime import datetime

from math import pi 

import pandas as pd

from .forms import SimulationModelForm
from .models import Simulation
from strategie.models import Strategie

import requests
from requests.exceptions import ConnectionError
from django.http import HttpResponse, JsonResponse
import json


class SimulationHinzufuegenView(CreateView):
    form_class = SimulationModelForm
    template_name = 'simulation/simulation_hinzufuegen.html'
    success_url = '/simulationen/' 

    def form_valid(self, form):
        return super().form_valid(form)    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['strategien'] = Strategie.objects.all()
        return context


class SimulationErgebnisView(View):
    template_name = 'simulation_ergebnis.html'
    
    def get(self,request):
        data = pd.DataFrame(MSFT)[:50]
        print(data.date)
        data["date"] = pd.to_datetime(data["date"])
        x = []
        y = []
        for i in range(50):
            y.append(i)
            x.append(i+100)
        print(y)
        data["date"] = y

        inc = data.close > data.open # if close bigger than open, store in inc to it can get green color
        dec = data.open > data.close
        w = 0.5 #12*60*60*1000 # half day in ms # this is the width of the bars

        TOOLS = "pan,wheel_zoom,box_zoom,reset,save"

        p = figure(x_axis_type="datetime", tools=TOOLS, plot_width=1000, title = "MSFT Candlestick")
        p.xaxis.major_label_orientation = pi/4 # how the labels are oriented on the x-axis, pi/4 means 45° tilted
        p.grid.grid_line_alpha=1 #the thickness of the grid-line

        p.segment(data.date, data.high, data.date, data.low, color="black")
        p.vbar(data.date[inc], w, data.open[inc], data.close[inc], fill_color="#11FF30", line_color="black")
        p.vbar(data.date[inc], w, data.open[inc], data.close[inc], fill_color="#11FF30", line_color="black") #vbar here has following attributes:
        # x: the x-coordinate, width, top-bar-value, bottom-bar-value, etc.
        p.vbar(data.date[dec], w, data.open[dec], data.close[dec], fill_color="#FF0000", line_color="black")
        p.line(y,x,line_color="orange", line_dash="4 4")



        script, div = components(p)
        return render(request, 'simulation/simulation_ergebnis.html', {'script':script, 'div':div})

class SimulationListeView(ListView):
    template_name = 'simulation/simulation_liste.html'
    def get_queryset(self):
        temp = versuche_request(self, None,"GET",None)
        if(temp==500):
            return {}
        return temp


class SimulationBearbeitenView(UpdateView):
    template_name = 'simulation/simulation_bearbeiten.html'  
    form_class = SimulationModelForm
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def form_valid(self, form):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,form,"PUT",id_)
        if(temp==500):
            return HttpResponse(fehler_message)    
        if(temp==200):
            return super().form_valid(form) 

class SimulationEntfernenView(DeleteView):
    template_name = 'simulation/simulation_entfernen.html' 
    #queryset = Article.objects.all() can be used for filtering the querried objects
    
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def get_success_url(self):
        return reverse('simulation:simulation-liste')


def versuche_request(outerself, form, http_methode, id):
    url = 'http://localhost:8001/regeln/'
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
            print(queryset.json())
        if(http_methode=="DELETE"):
            url = 'http://localhost:8001/regeln/entfernen/'+ str(id)+"/"
            queryset = requests.get(url)
        
    except ConnectionError as e:
        return 500
    if(id !=None and http_methode=="GET"):
        jsonObjekt = json.loads(queryset.text)
        objektFuerDarstellung = Regel()
        for key in jsonObjekt.keys(): 
            if key in dir(objektFuerDarstellung):
                setattr(objektFuerDarstellung,key,jsonObjekt[key])
        return objektFuerDarstellung
    return 200


# def test(request):
#     x = [1,2,3,4,5]
#     y = [1,2,3,9,10]
#     title = "my graph"

#     plot = figure(title= title,
#         x_axis_label = "H a L",
#         y_axis_label = " ijasdijajsd",    
#         plot_width=700,
#         plot_height=700,
#         #tools="",
#         #toolbar_location = None,
#     )

#     cr = plot.circle(
#         x,y, 
#         size=10, 
#         color="blue", 
#         fill_color="grey", 
#         hover_fill_color="firebrick",
#         fill_alpha=0.05, 
#         hover_alpha=0.3,
#         line_color=None, 
#         hover_line_color="white"
#         )
#     plot.add_tools(HoverTool(tooltips=None, renderers=[cr], mode='hline'))
#     plot.title.text_font_size = '20pt'
#     plot.line(x,y, legend = 'Learning Line', line_width = 4, line_color= "brown", line_dash = 'dashed')
#     plot.background_fill_color = "lightgrey"
#     plot.border_fill_color = "whitesmoke"
#     plot.min_border_left = 40
#     plot.min_border_right = 40
#     plot.outline_line_width = 7
#     plot.outline_line_alpha = 0.2
#     plot.outline_line_color = "purple"

#     script, div = components(plot)
#     return render(request, 'simulation/simulation_einstellung.html', {'script':script, 'div':div})

# def starter(request):
#     plot = figure()
#     plot.circle([1,10,35,27], [0,0,0,0], size = 20, color="blue")
#     # first list contains the x coordinates, the second contains the y coordinates
#     script, div = components(plot) # returns a <script> that contains the data of our flot along with a <div> to allow the plot to be loaded into HTML page
#     # Note: ensure you dont have any css on the div that would hide it from view

#     return render(request, "simulation/simulation_einstellung.html",{'script': script, 'div':div})