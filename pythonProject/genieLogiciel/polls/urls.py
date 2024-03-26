from django.urls import path
from . import views, viewsCourse

urlpatterns = [
    path("course/", views.home, name="home"),
    path("course/<str:code>/topics/", viewsCourse.topics, name="topics"),
    path("course/<str:code>/new/", viewsCourse.addTopic, name="addTopic"),
    #path("course/<str:code>/new/",viewsCourse.addTopic,name="submitTopic"),
    path("topic/", viewsCourse.topics, name="topic"),
    path("", views.login, name="login"),
    path("ok/",viewsCourse.ok,name="ok"),
    path("logout/", views.logout, name="logout"),
]
