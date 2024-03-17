from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("cours", views.cours, name="cours"),
    path("ok",views.ok,name="ok")
]
