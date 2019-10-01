"""gnosis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.urls import path
from notes import views as note_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('catalog/', include('catalog.urls')),
    path('home/', include('home.urls')),
    path('bookmarks/', include('bookmark.urls')),
    # the next one redirects the root URL to host/catalog/
    # change this as necessary later, maybe make it redirect to a welcome page
    path('', RedirectView.as_view(url='/home/')),
]

# for user authentication
urlpatterns += [
    url(r'^accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]

# Use static() to add url mapping to serve static files during development (only)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add url pattern for note app
urlpatterns += [
    path('note/create/', note_views.note_create, name='note_create'),
    path('note/<int:id>/update', note_views.note_update, name='note_update'),
    path('note/<int:id>/delete', note_views.note_delete, name='note_delete'),
]