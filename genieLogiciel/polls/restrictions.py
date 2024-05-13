from django.core.exceptions import PermissionDenied
from .queries import find_owner_of_ue, find_ue, find_students_of_ue

"""
Le script suivant permet de définir des décorateurs qui permettent de restreindre l'accès à certaines vues
"""


def admin_required(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un administrateur
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "admin" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def prof_or_superviseur_required(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un professeur ou un superviseur.
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "superviseur" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def prof_or_superviseur_or_student_required(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un professeur, un superviseur ou un étudiant.
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
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
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un étudiant.
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "etudiant" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def admin_or_professor_required(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un administrateur ou un professeur.
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "admin" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def admin_or_professor_or_superviseur_required(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un administrateur, un professeur ou un superviseur.
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "professeur" in request.user.role['role'] or "admin" in request.user.role['role'] or "superviseur" in \
                request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_owner_of_ue_or_admin(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas le propriétaire de l'ue, donc,
     le professeur en charge de celle-ci ou un administrateur
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "admin" in request.user.role['role'] or request.user == find_owner_of_ue(find_ue(kwargs['idue'])):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_student_of_ue(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas un étudiant inscrit à l'ue
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "etudiant" in request.user.role['role'] and request.user in find_students_of_ue(find_ue(kwargs['idue'])):
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def is_owner_of_ue_or_admin_or_student(function):
    """
    Décorateur permettant d'interdire l'accès à une vue si l'on n'est pas le propriétaire de l'ue, donc,
        le professeur en charge de celle-ci, un administrateur ou un étudiant inscrit à l'ue
    :param function: La fonction, vue à laquelle on tente d'accéder.
    :return: L'autorisation d'accéder à la fonction ou erreur le cas échéant.
    """
    def wrap(request, *args, **kwargs):
        if "admin" in request.user.role['role'] or request.user == find_owner_of_ue(
                find_ue(kwargs['idue'])) or "etudiant" in request.user.role['role']:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied()

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
