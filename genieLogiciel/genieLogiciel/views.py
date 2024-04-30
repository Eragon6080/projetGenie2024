from django.http import HttpRequest
from django.shortcuts import redirect, render



def redirect_to_polls(request) -> HttpRequest:
    return redirect("/polls")


