from django.contrib.auth.mixins import UserPassesTestMixin


class AuthorRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict actions to the author of the object."""

    def check_author(self):
        obj = self.get_object()
        return obj.user == self.request.user


    def test_func(self):
        return self.check_author()
