from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q
from .models import Post
from .serializers import PostSerializer
from .permissions import IsAuthorOrReadOnly

class PostViewSet(viewsets.ModelViewSet):
    """
    /api/posts/        GET list, POST create
    /api/posts/{id}/   GET retrieve, PUT/PATCH update (author), DELETE (author)
    Supports: ?search=, ?ordering=, ?user=, ?active=1
    """
    serializer_class = PostSerializer
    queryset = Post.objects.select_related("user").all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "text", "user__email", "user__username"]
    ordering_fields = ["created_at", "likes_count"]
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        user_id = self.request.query_params.get("user")
        if user_id:
            qs = qs.filter(user_id=user_id)
        active = self.request.query_params.get("active")
        if active in {"0","1","true","false"}:
            qs = qs.filter(is_active=active in {"1","true"})
        q = self.request.query_params.get("q")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(text__icontains=q))
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
