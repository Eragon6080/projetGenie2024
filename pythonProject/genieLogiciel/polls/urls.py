from django.urls import path
from . import views, viewsTopic

urlpatterns = [
    path("course/", views.home, name="home"),
    path("course/<str:code>/topics/", viewsTopic.topics, name="topics"),
    path("course/<str:code>/new/", views.addTopic, name="addTopic"),
    path("ok/",views.ok,name="ok"),
    #path("topic/",viewsTopic.topic,name="topic"),
    path("", views.login, name="login"),
]
