from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("", views.InboxView.as_view(), name="inbox"),
    path("c/<int:conversation_id>/", views.ConversationDetailView.as_view(), name="conversation_detail"),
    path("c/<int:conversation_id>/send/", views.ConversationSendMessageView.as_view(), name="send_message"),
    path("start/<int:user_pk>/", views.StartDMView.as_view(), name="start_dm"),
    path("mark-read/<int:conversation_id>/", views.MarkReadView.as_view(), name="mark_read"),
]
