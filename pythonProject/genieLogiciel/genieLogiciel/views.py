from django.http import HttpRequest
from django.shortcuts import redirect


def redirectToPolls(request)->HttpRequest:
    return redirect("/polls")