from rest_framework import permissions
from .models import User
from ad.models import Ad

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.roles.filter(name='admin').exists())
    

class IsPerformer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.roles.filter(name='performer').exists())

    
class IsAdOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Ad):
            return obj.owner == request.user
        return False

class IsAdPerformer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Ad):
            return obj.performer == request.user
        return False

class IsSupportUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.roles.filter(name='support').exists())
    
class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        result = bool(request.user and request.user.is_authenticated and request.user.roles.filter(name='customer').exists())
        return result
    
    

# class IsOnlyCustomer(permissions.BasePermission):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_authenticated and request.user.roles.filter(name='customer').exists() and not request.user.roles.filter(name='performer').exists())



    
