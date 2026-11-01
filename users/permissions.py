from rest_framework import permissions


class IsSelfOrReadOnly(permissions.BasePermission):
    """Просмотр доступен авторизованным пользователям.

    Изменение и удаление разрешены только владельцу профиля.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.pk == request.user.pk


class IsModerator(permissions.BasePermission):
    """Проверяет принадлежность пользователя к группе moderators."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="moderators").exists()
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsOwner(permissions.BasePermission):
    """Разрешает доступ только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and obj.owner_id == request.user.pk
