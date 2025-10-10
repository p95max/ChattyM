from django.urls import path
from . import views

app_name = "subscriptions"

urlpatterns = [
    path("toggle/<int:user_pk>/", views.ToggleSubscriptionView.as_view(), name="toggle"),
    path("followers/<int:user_pk>/", views.FollowersListView.as_view(), name="followers"),
    path("following/<int:user_pk>/", views.FollowingListView.as_view(), name="following"),
]
