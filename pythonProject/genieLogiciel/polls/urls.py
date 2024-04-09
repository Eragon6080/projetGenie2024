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
    path("admin/role/",adminViews.role,name="role"),
     path("suivi/",views.yes,name="yes"),
     path('sujet/edit/<int:sujet_id>/', courseViews.editTopic, name='edit_topic'),
    path('sujet/delete/<int:sujet_id>/', courseViews.deleteTopic, name='delete_topic'),
    path('course/<str:idue>/gestion/', courseViews.gestion_etape, name='gestion_etape'),
    path("course/<str:idue>/steps/", courseViews.afficher_etapes_ue, name="steps"),
]
