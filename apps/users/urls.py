from django.urls import path
from . import views

app_name = "users"

# urlpatterns = [
#     path("signup/", views.SignUpView.as_view(), name="signup"),
#     path("login/", views.LoginView.as_view(), name="login"),
#     path("me/", views.ProfileView.as_view(), name="me"),
#     path("<int:pk>/", views.UserDetailView.as_view(), name="detail"),
# ]