from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView
)
from .forms import StrategieModelForm
from .models import Strategie
from regel.models import Regel

class StrategieErstellenView(CreateView):
    
    template_name = 'strategie/strategie_erstellen.html'
    form_class = StrategieModelForm
    success_url = '/strategien/' 
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['regeln'] = Regel.objects.all()
        return context

    def form_valid(self, form):
        return super().form_valid(form)
    

class StrategieListeView(ListView):
    template_name = 'strategie/strategie_liste.html'  # with this command we can set a new path to our templates
    queryset = Strategie.objects.all() # since its a ListView, Django will look for template <blog>/<modelname>_list.html

class StrategieDetailView(DetailView):
    template_name = 'strategie/strategie_detail.html' 
    #queryset = Article.objects.all() #can be used for filtering the querried objects

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Strategie, id=id_)

class StrategieBearbeitenView(UpdateView):
    template_name = 'strategie/strategie_bearbeiten.html'  
    form_class = StrategieModelForm
    queryset = Strategie.objects.all()
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Strategie, id=id_)

    def form_valid(self, form):
        #TODO add redirect after succesful update or confirmation?
        return super().form_valid(form)

class StrategieEntfernenView(DeleteView):
    template_name = 'strategie/strategie_entfernen.html' 
    #queryset = Article.objects.all() can be used for filtering the querried objects
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Strategie, id=id_)

    def get_success_url(self):
        return reverse('strategie:strategie-liste')