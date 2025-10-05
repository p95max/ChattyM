from django.urls import path, re_path
from . import views

app_name = "users"

urlpatterns = [
    path("me/", views.MyProfileView.as_view(), name="my_profile"),
    re_path(r"^(?P<username>(?!me$)[A-Za-z0-9_.-]+)/$", views.ProfileView.as_view(), name="author_profile"),
]
