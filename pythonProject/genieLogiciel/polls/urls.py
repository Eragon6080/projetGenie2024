from django.urls import path
from . import views, viewsCourse

urlpatterns = [
    path("course/", views.home, name="home"),
    path("course/<str:code>/topics/", viewsCourse.topics, name="topics"),
    path("course/<str:code>/new/", viewsCourse.addTopic, name="addTopic"),
    path("ok/",views.ok,name="ok"),
    #path("topic/",viewsTopic.topic,name="topic"),
    path("", views.login, name="login"),
]
