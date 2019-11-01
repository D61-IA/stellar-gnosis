from django.urls import path
from . import views

# for creating/deleting/searching Bookmarks
urlpatterns = [
    path('', views.bookmarks, name='bookmarks'),
    path('search', views.search_bookmarks, name='search_bookmarks'),
    path('delete/<int:id>', views.bookmark_delete, name='bookmark_delete')
]
