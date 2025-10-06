from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    """
    Simple comment form. 'parent' is hidden (filled by JS when replying).
    """
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Write your comment..."}),
        max_length=2000,
        label="",
    )

    class Meta:
        model = Comment
        fields = ("content", "parent")
        widgets = {
            "parent": forms.HiddenInput(),
        }
