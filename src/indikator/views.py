from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView
)
from .forms import IndikatorModelForm
from .models import Indikator
import requests

class IndikatorErstellenView(CreateView):
    
    template_name = 'indikator/indikator_erstellen.html'
    form_class = IndikatorModelForm
    queryset = Indikator.objects.all()
    success_url = '/indikatoren/' 


    def form_valid(self, form):
        # try:
        #     r = requests.post('http://localhost:8001/indikatoren/', data=form.cleaned_data)
        # except ConnectionError:
            
        # console.log(r.status_code)
        return super().form_valid(form)
    

class IndikatorListeView(ListView):
    template_name = 'indikator/indikator_liste.html'  # with this command we can set a new path to our templates
    # queryset = requests.get('http://localhost:8001/indikatoren/').json() # since its a ListView, Django will look for template <blog>/<modelname>_list.html
    queryset = Indikator.objects.all()

class IndikatorDetailView(DetailView):
    template_name = 'indikator/indikator_detail.html' 
    #queryset = Article.objects.all() #can be used for filtering the querried objects

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Indikator, id=id_)
        # url = 'http://localhost:8001/indikatoren/'+id_
        # return requests.get(url)

class IndikatorBearbeitenView(UpdateView):
    template_name = 'indikator/indikator_bearbeiten.html'  
    form_class = IndikatorModelForm
    queryset = Indikator.objects.all()
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Indikator, id=id_)

    def form_valid(self, form):
        #TODO add redirect after succesful update or confirmation?
        return super().form_valid(form)

class IndikatorEntfernenView(DeleteView):
    template_name = 'indikator/indikator_entfernen.html' 
    #queryset = Article.objects.all() can be used for filtering the querried objects
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Indikator, id=id_)

    def get_success_url(self):
        return reverse('indikator:indikator-liste')