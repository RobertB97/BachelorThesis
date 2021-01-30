from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.views.generic import (
    CreateView,
    ListView,
    DetailView,  
    UpdateView,
    DeleteView
)

# views.py is responsible for the logic of the User Interface
# all the input data is currently being stored in the django-db but will be replaced with mr. galm's influxdb 


from .forms import RegelModelForm
from .models import Regel

class RegelErstellenView(CreateView):
    
    template_name = 'regel/regel_erstellen.html'
    form_class = RegelModelForm
    queryset = Regel.objects.all()
    success_url = '/regeln/' 

    def form_valid(self, form):
        return super().form_valid(form)    
            

class RegelListeView(ListView):
    template_name = 'regel/regel_liste.html'  # with this command we can set a new path to our templates
    queryset = Regel.objects.all() # since its a ListView, Django will look for template <blog>/<modelname>_list.html

class RegelDetailView(DetailView):
    template_name = 'regel/regel_detail.html' 
    #queryset = Article.objects.all() can be used for filtering the querried objects

    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Regel, id=id_)

class RegelBearbeitenView(UpdateView):
    template_name = 'regel/regel_bearbeiten.html'  
    form_class = RegelModelForm
    queryset = Regel.objects.all()
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Regel, id=id_)

    def form_valid(self, form):
        return super().form_valid(form)

class RegelEntfernenView(DeleteView):
    template_name = 'regel/regel_entfernen.html' 
    #queryset = Article.objects.all() can be used for filtering the querried objects
    
    def get_object(self):
        id_ = self.kwargs.get("id")
        return get_object_or_404(Regel, id=id_)

    def get_success_url(self):
        return reverse('regel:regel-liste')