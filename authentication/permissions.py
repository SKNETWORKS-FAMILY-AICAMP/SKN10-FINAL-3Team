from rest_framework.permissions import BasePermission
from user.models import Role

# 스템프 유저만 접근 허용
class IsStampUser(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_stamp_user
            )

# 파트너만 접근 허용
class IsPartner(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_partner
        )