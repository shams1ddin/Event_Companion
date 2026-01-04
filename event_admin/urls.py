from django.contrib import admin
from django.http import HttpResponse
from django.urls import path

import config

urlpatterns = [
    path('admin/', admin.site.urls),
]
