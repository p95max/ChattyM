"""Root URL configuration for the project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from apps.posts.views_api import PostViewSet


router = DefaultRouter()

router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("apps.core.urls", namespace="core")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("posts/", include("apps.posts.urls", namespace="posts")),
    path("comments/", include("apps.comments.urls", namespace="comments")),
    path("likes/", include("apps.likes.urls", namespace="likes")),
    path("subscriptions/", include("apps.subscriptions.urls", namespace="subscriptions")),
    path("messages/", include("apps.messaging.urls", namespace="messages")),
    path("notifications/", include("apps.notifications.urls", namespace="notifications")),

    path("api/", include(router.urls)),
]

try:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
        path(
            "api/docs/",
            SpectacularSwaggerView.as_view(url_name="schema"),
            name="swagger-ui",
        ),
    ]
except Exception:
    pass

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)