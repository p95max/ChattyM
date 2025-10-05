from django.urls import path
from . import views
from . import forms


app_name = "posts"

urlpatterns = [
    path("", views.PostListView.as_view(), name="list"),
    path("<int:pk>/", views.PostDetailView.as_view(), name="detail"),
    path("my-posts/", views.UserPostsView.as_view(), name="user_posts"),

    path("create/", forms.PostCreateView.as_view(), name="create"),
    path("<int:pk>/edit/", forms.PostUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", forms.PostDeleteView.as_view(), name="delete"),
]