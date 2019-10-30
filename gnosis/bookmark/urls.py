from django.urls import path
from . import views

# for updating/creating a Endorsement
urlpatterns = [
    path('', views.bookmarks, name='bookmarks'),
    path('search', views.search_bookmarks, name='search_bookmarks')
]
