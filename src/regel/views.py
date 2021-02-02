from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView
)

from .forms import RegelModelForm
from .models import Regel
import requests
from requests.exceptions import ConnectionError
from django.http import HttpResponse, JsonResponse
import json


fehler_message = "Hoppla, da ist wohl etwas schiefgelaufen"

class RegelHinzufuegenView(CreateView):   
    template_name = 'regel/regel_hinzufuegen.html'
    form_class = RegelModelForm
    success_url = '/regeln/' 
    #queryset = Indikator.objects.all() # ohne api
    
    def form_valid(self, form):
        temp = versuche_request(self,form,"POST",None)
        if(temp==500):
            return HttpResponse(fehler_message)
        if(temp==200):
            return super().form_valid(form) 
        
class RegelListeView(ListView):
    template_name = 'regel/regel_liste.html'
    
    def get_queryset(self):
        temp = versuche_request(self, None,"GET",None)
        if(temp==500):
            return {}
        return temp

class RegelDetailView(DetailView):
    template_name = 'regel/regel_detail.html' 

    def get_object(self):
        id_ = self.kwargs.get("id")
        antwort = versuche_request(self,None,"GET",id_)
        return antwort

class RegelBearbeitenView(UpdateView):
    template_name = 'regel/regel_bearbeiten.html'  
    form_class = RegelModelForm
    
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

class RegelEntfernenView(DeleteView):
    template_name = 'regel/regel_entfernen.html' 
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def get_success_url(self):
        return reverse('regel:regel-liste')

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