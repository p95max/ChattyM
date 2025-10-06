from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import JsonResponse, HttpResponseForbidden

class AuthorRequiredMixin(UserPassesTestMixin):
    """
    Ensure that only the object's author (obj.user or obj.author) or staff/superuser may proceed.

    - test_func returns True for the object's owner, staff or superuser.
    - handle_no_permission returns JSON 403 if request is AJAX, else HttpResponseForbidden.
    """

    def test_func(self):
        try:
            obj = self.get_object()
        except Exception:
            return False

        user = getattr(self.request, "user", None)
        if not user or not user.is_authenticated:
            return False

        owner = getattr(obj, "user", None) or getattr(obj, "author", None)
        if owner and owner == user:
            return True

        if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
            return True

        return False

    def handle_no_permission(self):
        if self.request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"status": "error", "detail": "forbidden"}, status=403)
        return HttpResponseForbidden("You don't have permission to perform this action.")
