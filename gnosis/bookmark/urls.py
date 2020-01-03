from django.urls import path
from . import views

# for creating/deleting/searching Bookmarks
urlpatterns = [
    path('', views.bookmarks, name='bookmarks'),
    path('search/', views.bookmark_search, name='bookmark_search'),
    path('delete/<int:id>/', views.bookmark_delete, name='bookmark_delete')
]
