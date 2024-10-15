from rest_framework import permissions
from .models import User, BankAccount, Card, Transaction ,BankAccountApplication, CardApplication

class IsLoggedIn(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return str(request.user) != 'AnonymousUser'

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role.admin_permission
    
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            if not obj.role.banker_permission:
                return False

        return True

class IsBankerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role.banker_permission

    
class IsClientUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role.client_permission


class ClientReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.role.client_permission
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not obj:
            return False
        
        # Validation for User object
        if isinstance(obj, User):
            if user.id == obj.id:
                return True
        # Validation for other objects linked to User
        if isinstance(obj, Transaction):
            return user.id == obj.bank_account.user.id
        else:
            return user.id == obj.user.id
    
class ClientApplicationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Clients can only create and view their applications
        if request.method == 'POST' or request.method == 'GET':
            return request.user and request.user.role.client_permission
        return False
    
    # Clients can only view their own applications
    def has_object_permission(self, request, view, obj):
        return request.user.id == obj.user.id

class BankerReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.role.banker_permission 

        return False
    
    
