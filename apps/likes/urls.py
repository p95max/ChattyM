from django.urls import path
from . import views

app_name = "likes"

urlpatterns = [
    path("<int:pk>/like/", views.ToggleLikeView.as_view(), name="toggle"),
]

