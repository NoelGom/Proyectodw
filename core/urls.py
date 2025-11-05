# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def root_redirect(request):
        return redirect("tienda:producto_list")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", root_redirect, name="root"),          
    path("", include(("tienda.urls", "tienda"), namespace="tienda")),  # app
]
