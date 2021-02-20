from django.db import models
from django.urls import reverse

from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField



class Indikator(models.Model):
  name               = models.CharField(max_length=50)
  beschreibung       = models.TextField()
  code               = RichTextUploadingField(config_name='special')
  nutzername         = models.CharField(max_length=30)
  
  def get_absolute_url(self):
    return reverse("indikator:indikator-details", kwargs={"id": self.id})
    
    