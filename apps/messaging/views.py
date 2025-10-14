from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from .models import Conversation, Participant, Message
from .forms import MessageForm
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest


class ParticipantRequiredMixin:
    """
    Mixin to ensure the request.user is participant of the conversation.
    Must be used on CBVs which have a 'conversation_id' kwarg or use get_object() returning Conversation.
    Sets self.conversation and self.participant.
    """
    def dispatch(self, request, *args, **kwargs):

        conv_id = kwargs.get("conversation_id") or (getattr(self, "object", None) and getattr(self.object, "pk", None))
        if not conv_id:

            if hasattr(self, "get_object"):
                try:
                    self.object = self.get_object()
                    conv_id = getattr(self.object, "pk", None)
                except Exception:
                    conv_id = None

        if not conv_id:
            return HttpResponseBadRequest("Conversation id missing")

        self.conversation = get_object_or_404(Conversation, pk=conv_id)
        try:
            self.participant = Participant.objects.get(conversation=self.conversation, user=request.user, is_active=True)
        except Participant.DoesNotExist:
            return HttpResponseForbidden("You are not a participant of this conversation")
        return super().dispatch(request, *args, **kwargs)


class InboxView(LoginRequiredMixin, ListView):
    """
    List of conversations for the current user.
    We list Conversation objects where user is a Participant.
    """
    model = Conversation
    template_name = "apps/messaging/inbox.html"
    context_object_name = "conversations"
    paginate_by = 30

    def get_queryset(self):

        last_msg_qs = Message.objects.filter(conversation=OuterRef("pk")).order_by("-created_at")
        qs = (
            Conversation.objects.filter(participants__user=self.request.user, participants__is_active=True)
            .distinct()
            .annotate(last_message_id=Subquery(last_msg_qs.values("id")[:1]),
                      last_message_at=Subquery(last_msg_qs.values("created_at")[:1]))
            .order_by("-last_message_at", "-created_at")
        )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        conversations = []
        for conv in ctx["conversations"]:
            last = None
            if getattr(conv, "last_message_id", None):
                last = Message.objects.filter(pk=conv.last_message_id).select_related("sender").first()
            conversations.append({
                "conversation": conv,
                "last_message": last,
                "unread": conv.unread_count_for(self.request.user),
            })
        ctx["conversations"] = conversations
        return ctx


class ConversationDetailView(LoginRequiredMixin, ParticipantRequiredMixin, FormMixin, DetailView):
    """
    Show conversation and message send form.
    GET  - render conversation
    POST - handled by the FormMixin (message sending) when posting to the same URL.
    For simpler routing we also provide separate send CBV below; but this class can accept POST as well.
    """
    model = Conversation
    template_name = "apps/messaging/conversation.html"
    context_object_name = "conversation"
    form_class = MessageForm
    pk_url_kwarg = "conversation_id"

    def get_object(self, queryset=None):
        conv = get_object_or_404(Conversation, pk=self.kwargs.get("conversation_id"))
        return conv

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.participant.last_read = timezone.now()
        self.participant.save(update_fields=["last_read"])
        return response

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        messages = self.conversation.messages.select_related("sender").order_by("created_at")
        ctx["messages"] = messages
        ctx["form"] = ctx.get("form") or self.get_form()
        return ctx

    def post(self, request, *args, **kwargs):
        """
        Support posting message to same URL. If you prefer separate send endpoint,
        leave this and use ConversationSendMessageView instead.
        """
        form = self.get_form()
        if not form.is_valid():
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"status": "error", "errors": form.errors}, status=400)
            return self.form_invalid(form)

        return self.form_valid(form)

    @transaction.atomic
    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.conversation = self.conversation
        msg.sender = self.request.user
        msg.save()
        Participant.objects.filter(conversation=self.conversation, user=self.request.user).update(last_read=timezone.now())

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "status": "ok",
                "message": {
                    "id": msg.pk,
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
            })
        return redirect(reverse("messaging:conversation_detail", args=[self.conversation.pk]))


class ConversationSendMessageView(LoginRequiredMixin, ParticipantRequiredMixin, FormView):
    """
    Dedicated CBV for POSTing a message to a conversation (useful for form action).
    Returns JSON on AJAX; otherwise redirect back to conversation detail.
    """
    form_class = MessageForm

    def form_invalid(self, form):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "errors": form.errors}, status=400)
        return super().form_invalid(form)

    @transaction.atomic
    def form_valid(self, form):
        msg = form.save(commit=False)
        msg.conversation = self.conversation
        msg.sender = self.request.user
        msg.save()
        Participant.objects.filter(conversation=self.conversation, user=self.request.user).update(last_read=timezone.now())

        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({
                "status": "ok",
                "message": {
                    "id": msg.pk,
                    "sender_id": msg.sender_id,
                    "content": msg.content,
                    "created_at": msg.created_at.isoformat(),
                }
            })
        return redirect(reverse("messaging:conversation_detail", args=[self.conversation.pk]))


class StartDMView(LoginRequiredMixin, View):
    """
    Find existing 1:1 conversation (exactly two active participants) or create a new one,
    then redirect to conversation detail.
    """
    def get(self, request, user_pk, *args, **kwargs):
        if request.user.pk == int(user_pk):
            return HttpResponseBadRequest("Cannot start chat with yourself")
        from django.contrib.auth import get_user_model
        User = get_user_model()
        target = get_object_or_404(User, pk=user_pk, is_active=True)

        convs = Conversation.objects.filter(participants__user=request.user).filter(participants__user=target).distinct()
        for c in convs:
            if c.participants.filter(is_active=True).count() == 2:
                return redirect(reverse("messaging:conversation_detail", args=[c.pk]))

        # create new conversation (1:1)
        with transaction.atomic():
            conv = Conversation.objects.create()
            Participant.objects.bulk_create([
                Participant(conversation=conv, user=request.user, last_read=timezone.now()),
                Participant(conversation=conv, user=target)
            ])
        return redirect(reverse("messaging:conversation_detail", args=[conv.pk]))


class MarkReadView(LoginRequiredMixin, ParticipantRequiredMixin, View):
    """
    Mark conversation as read for current user (POST).
    """
    def post(self, request, *args, **kwargs):
        self.participant.last_read = timezone.now()
        self.participant.save(update_fields=["last_read"])
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "ok"})
        return redirect(reverse("messaging:conversation_detail", args=[self.conversation.pk]))
