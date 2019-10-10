from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_index, name='note_index'),
]