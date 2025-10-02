"""URLs for core app (homepage, static pages)."""
from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.main, name="main"),
]