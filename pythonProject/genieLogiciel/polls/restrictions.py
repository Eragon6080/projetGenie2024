from django.http import HttpResponseForbidden
from django.core.exceptions import PermissionDenied
from .queries import find_owner_of_ue, find_ue


def admin_required(function):
    def wrap(request, *args, **kwargs):
        if "admin" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def prof_or_superviseur_required(function):
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "superviseur" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



def prof_or_superviseur_or_student_required(function):
    def wrap(request, *args, **kwargs):
        if ("etudiant" in request.user.role['role'] or "professeur" in request.user.role['role'] or
                "superviseur" in request.user.role['role']):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def student_required(function):
    def wrap(request, *args, **kwargs):
        if "etudiant" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def admin_or_professor_required(function):
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "admin" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def admin_or_professor_or_superviseur_required(function):
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "admin" in request.user.role['role'] or "superviseur" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def is_owner_of_ue_or_admin(function):
    def wrap(request, *args, **kwargs):
        if "admin" in request.user.role['role'] or request.user == find_owner_of_ue(find_ue(kwargs['idue'])).first():
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap



