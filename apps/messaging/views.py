from django.db import transaction
from django.db.models import OuterRef, Subquery, Count
from django.utils import timezone
from django.views.generic import ListView, DetailView, FormView
from django.views.generic.edit import FormMixin
from .models import Conversation, Participant, Message
from .forms import MessageForm
from django.http import JsonResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseServerError
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from .models import Conversation

User = get_user_model()

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

    def post(self, request, user_pk, *args, **kwargs):
        recipient = get_object_or_404(User, pk=user_pk, is_active=True)

        if recipient == request.user:
            return HttpResponseBadRequest("Cannot start a conversation with yourself.")

        conv_qs = (
            Conversation.objects
            .annotate(num_participants=Count("participants"))
            .filter(num_participants=2)
            .filter(participants__user=request.user)
            .filter(participants__user=recipient)
        )
        conversation = conv_qs.first()

        if conversation is None:
            with transaction.atomic():
                conversation = Conversation.objects.create()
                Participant.objects.create(conversation=conversation, user=request.user)
                Participant.objects.create(conversation=conversation, user=recipient)

        subject = (request.POST.get("subject") or "").strip()
        body = (request.POST.get("body") or "").strip()

        if not body:
            return redirect("messages:conversation_detail", conversation_id=conversation.pk)

        try:

            conv_field = None
            sender_field = None
            for f in Message._meta.get_fields():
                if getattr(f, "is_relation", False) and getattr(f, "related_model", None) is Conversation:
                    conv_field = f.name
                if getattr(f, "is_relation", False) and getattr(f, "related_model", None) is User:
                    sender_field = f.name

            possible_body_names = ("body", "content", "text", "message", "message_text", "body_text")
            possible_subject_names = ("subject", "title", "topic", "thread_subject")

            model_field_names = {f.name for f in Message._meta.get_fields() if getattr(f, "concrete", False)}

            body_field = next((n for n in possible_body_names if n in model_field_names), None)
            subject_field = next((n for n in possible_subject_names if n in model_field_names), None)

            create_kwargs = {}
            if conv_field:
                create_kwargs[conv_field] = conversation
            elif "conversation" in model_field_names:
                create_kwargs["conversation"] = conversation

            if sender_field:
                create_kwargs[sender_field] = request.user
            elif "sender" in model_field_names:
                create_kwargs["sender"] = request.user
            elif "author" in model_field_names:
                create_kwargs["author"] = request.user

            if body_field:
                create_kwargs[body_field] = body
            else:
                fallback_text_field = next((n for n in ("text", "content", "body", "message") if n in model_field_names), None)
                if fallback_text_field:
                    create_kwargs[fallback_text_field] = body
                else:
                    return HttpResponseServerError("Message model has no text field to store body.")

            if subject_field and subject:
                create_kwargs[subject_field] = subject
            Message.objects.create(**create_kwargs)

        except Exception as e:
            return HttpResponseServerError(f"Failed to create message: {e}")

        return redirect("messages:conversation_detail", conversation_id=conversation.pk)



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
