from django import forms
from allauth.account.forms import LoginForm, SignupForm


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            input_type = getattr(widget, "input_type", "")
            if input_type == "checkbox":
                widget.attrs.update({"class": "form-check-input"})
            else:
                widget.attrs.update({
                    "class": "form-control",
                    "placeholder": field.label,
                    "autocomplete": widget.attrs.get("autocomplete", "on"),
                })


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            input_type = getattr(widget, "input_type", "")
            if input_type == "checkbox":
                widget.attrs.update({"class": "form-check-input"})
            else:
                widget.attrs.update({
                    "class": "form-control",
                    "placeholder": field.label,
                    "autocomplete": widget.attrs.get("autocomplete", "on"),
                })