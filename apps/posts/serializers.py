from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.id")
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "user", "title", "text", "image",
            "likes_count", "is_active", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "likes_count", "created_at", "updated_at"]
