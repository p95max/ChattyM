from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path("add/<int:post_pk>/", views.AddCommentView.as_view(), name="add"),
    path("edit/<int:pk>/", views.EditCommentView.as_view(), name="edit"),
    path("delete/<int:pk>/", views.DeleteCommentView.as_view(), name="delete"),
]
