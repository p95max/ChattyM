from rest_framework import serializers
from .models import Conversation, Message, Participant
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.ReadOnlyField(source='sender.id')

    class Meta:
        model = Message
        fields = ("id","conversation","sender","content","created_at","is_deleted")
        read_only_fields = ("id","sender","created_at","is_deleted")
