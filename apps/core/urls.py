"""URLs for core app (homepage, static pages)."""
from django.urls import path
from apps.core import views

app_name = "core"

urlpatterns = [
    path("", views.MainView.as_view(), name="main"),
]