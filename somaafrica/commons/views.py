import logging

from rest_framework import exceptions


LOGGER = logging.getLogger(__name__)


class CustomDjangoModelPermissions(object):

    def get_required_permissions(self, method, view):
        """
        Given a model and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        perms_map = getattr(view, "perms_map", None)
        if perms_map is None:
            return

        if method not in view.perms_map:
            raise exceptions.MethodNotAllowed(method)

        return view.perms_map[method]

    def has_permission(self, request, view):
        # pdb.set_trace()
        if not request.user or not request.user.is_authenticated:
            return False

        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, '_ignore_model_permissions', False):
            return True

        perms = self.get_required_permissions(request.method, view)

        if perms is None or not len(perms):
            return True

        return request.user.has_perms(perms)

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
