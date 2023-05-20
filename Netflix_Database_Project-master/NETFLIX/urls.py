"""NETFLIX URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib import admin
from django.conf.urls import include,url
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static
from streaming import views as views_stream


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^user/', include('accounts.urls')),
    path('', include('home.urls')),
    path('stream/stream_shows/<str:file_name>/', views_stream.stream_video, name="stream_show"),
    path('stream/download_shows/<str:file_name>/', views_stream.download_video, name="download_show"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
