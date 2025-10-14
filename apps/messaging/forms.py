from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write a message..."}),
        max_length=4000,
        label=""
    )

    class Meta:
        model = Message
        fields = ("content",)
