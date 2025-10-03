"""Root URL configuration for the project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),  # ok
    path("", include("apps.core.urls", namespace="core")),
    path("users/", include("apps.users.urls", namespace="users")),
    path("posts/", include("apps.posts.urls", namespace="posts")),
    path("comments/", include("apps.comments.urls", namespace="comments")),
    path("likes/", include("apps.likes.urls", namespace="likes")),
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