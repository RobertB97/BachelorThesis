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
from django.conf import settings


fehler_message = "Hoppla, da ist wohl etwas schiefgelaufen"

class RegelHinzufuegenView(CreateView):   
    template_name = 'regel/regel_hinzufuegen.html'
    form_class = RegelModelForm
    success_url = '/regeln/' 

    def form_valid(self, form):
        #return generischer_request(true,self,form.cleaned_data,"POST"):
        # queryset = requests.post(url, data=daten).json()
        form.cleaned_data['nutzername'] = self.request.user.username
        temp = versuche_request(self,form,"POST",None)
        if(temp==500):
            return HttpResponse(fehler_message)
        if(temp==200):
            return super().form_valid(form) 
        
class RegelListeView(ListView):
    template_name = 'regel/regel_liste.html'

    def get_queryset(self):
        #return generischer_request(false,self,None,"POST"):
        temp = versuche_request(self, None,"GET",None)
        if(temp==500):
            return {}
        return temp

class RegelDetailView(DetailView):
    template_name = 'regel/regel_detail.html' 

    def get_object(self):
        #return generischer_request(true,self,None,"POST"):
        id_ = self.kwargs.get("id")
        antwort = versuche_request(self,None,"GET",id_)
        return antwort

class RegelBearbeitenView(UpdateView):
    template_name = 'regel/regel_bearbeiten.html'  
    form_class = RegelModelForm
    
    def get_object(self):
        #return generischer_request(true,self,None,"POST"):
        id_ = self.kwargs.get("id")
        
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def form_valid(self, form):
        #return generischer_request(true,self,form.cleaned_data,"PUT"):
        id_ = self.kwargs.get("id")
        form.cleaned_data['nutzername'] = self.request.user.username
        temp = versuche_request(self,form,"PUT",id_)
        if(temp==500):
            return HttpResponse(fehler_message)    
        if(temp==200):
            return super().form_valid(form) 

class RegelEntfernenView(DeleteView):
    template_name = 'regel/regel_entfernen.html' 

    def get_object(self):
        #return generischer_request(true,self,None,"POST"):
        id_ = self.kwargs.get("id")
        temp = versuche_request(self,None,"GET",id_)
        if(temp == 500):
            return HttpResponse(fehler_message)
        return temp

    def get_success_url(self):
        return reverse('regel:regel-liste')

def versuche_request(outerself, form, http_methode, id):
    url = settings.API_SERVER_URL + '/regeln/'
    print(url)
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
        if(http_methode=="POST"): # POST wird beim erstellen und holen verwendet
            queryset = requests.post(url, data=daten)
        if(http_methode=="PUT"): # PUT wird beim verändern und löschen verwendet
            queryset = requests.put(url, data=daten)
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

    """
    def generischer_request(brauchtID,outerself,daten,http_methode):
        if(brauchtID): # Wenn Id gebraucht wird, wird sie geholt, ansonsten None gesetzt
            id = self.kwargs.get("id")
        else:
            id = None,

        daten = {
            "id": id,
            "nutzername": outerself.request.session['nutzername'],
            "daten": daten
        }
        try:
        if(http_methode == "POST"): # für List oder Detail
            antwort = requests.post(url,daten)
            if(id==None): 
                # List ruft die Methode ohne ID auf, da alle Objekte gebraucht werden. 
                # Die request-Antwort muss vorher in JSON umgewandelt werden um Daten korrekt darstellen zu können
                return antwort.json()
        if(http_methode == "PUT"): # für Update oder Delete, bei Delete ist Daten leer
            antwort = requests.put(url,daten)
        except ConnectionError as e:
            if(id==None):
                return {}
            else:
                return HttpResponse(fehler_message)
        return antwort

    """