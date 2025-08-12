from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
