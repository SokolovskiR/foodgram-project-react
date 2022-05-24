from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class AutoAddAuthorEditorMixin:
    """Mixin to add author/editor automatically on create/update."""

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(author=user, last_editor=user)

    def perform_update(self, serializer):
        user = self.request.user
        serializer.save(last_editor=user)


class ListRetrieveMixin(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """Mixin for retrieve and list actions."""


class DestroyMixin:
    """Mixin with destroy method to delete object from db."""

    def destroy(self, request, *args, **kwargs):
        qs = self.get_queryset()
        lookup_field = self.lookup_field
        lookup_kwargs = {self.lookup_field: self.kwargs.get(lookup_field)}
        obj = qs.filter(**lookup_kwargs).first()
        if not obj:
            return Response(
                {'errors': 'этого объекта нет в списке'},
                status=status.HTTP_400_BAD_REQUEST
            )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
