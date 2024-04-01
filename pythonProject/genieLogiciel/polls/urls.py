from django.urls import path
from . import views, courseViews, adminViews

urlpatterns = [
    path("course/", views.home, name="home"),
    path("course/<str:code>/topics/", courseViews.topics, name="topics"),
    path("course/<str:code>/new/", courseViews.addTopic, name="addTopic"),
    path("topic/", courseViews.topics, name="topic"),
    path("", views.login, name="login"),
    path("ok/",courseViews.ok,name="ok"),
    path("logout/", views.logout, name="logout"),
    path("admin/",adminViews.admin,name="admin"),
    path("admin/role/",adminViews.role,name="role")
]
