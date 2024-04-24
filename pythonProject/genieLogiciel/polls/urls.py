from django.urls import path
from . import views, courseViews, adminViews

urlpatterns = [
    path("course/", views.home, name="home"),
    path("course/<str:idue>/", views.course, name="course"),
    path("course/<str:idue>/topics/", courseViews.topics, name="topics"),
    path("course/<str:idue>/my/topics/", courseViews.myTopics, name="myTopics"),
    path("course/<str:idue>/new/", courseViews.addTopic, name="addTopic"),
    path("course/<str:idue>/participants/", courseViews.participants, name="participants"),
    path("topic/", courseViews.topics, name="topic"),
    path("home/",views.accueil,name="accueil"),
    path("", views.login, name="login"),
    path("ok/", courseViews.ok, name="ok"),
    path("logout/", views.logout, name="logout"),
    path("admin/", adminViews.admin, name="admin"),
    path("admin/role/", adminViews.role, name="role"),
    path("admin/role/<str:view>", adminViews.role, name="roleView"),
    path("admin/courses/", adminViews.courses, name="coursSummary"),
    path("suivi/", views.yes, name="yes"),
    path("profile/", views.profile, name="profile"),
    path("fiche/<int:idpersonne>", views.fiche, name="fiche"),
    path('sujet/edit/<int:sujet_id>/', courseViews.editTopic, name='edit_topic'),
    path('sujet/delete/<int:sujet_id>/', courseViews.deleteTopic, name='delete_topic'),
    path('course/<str:idue>/gestion/', courseViews.gestion_etape, name='gestion_etape'),
    path("course/<str:idue>/steps/", courseViews.afficher_etapes_ue, name="steps"),
    path("course/inscription",courseViews.inscription,name="inscription"),
    path("course/inscription/<str:idue>/<str:nom>",courseViews.inscriptionValidation,name="inscription"),
    path("course/mycourses",courseViews.mycourses,name="mycourses"),
    path("switch_role/<str:role>", views.switchRole, name="switch_role"),
    path("echeance/",views.echeance,name="echeance"),
    path("echeance/<int:delivrable_id>",views.upload_delivrable,name="delivrable"),
    path("sujet/reservation",courseViews.reservation,name="reservation"),
    path("sujet/reservation/<int:idsujet>", courseViews.reservationValidation, name="reservation"),
    path("sujet/reservation/confirmation/<int:idsujet>",courseViews.reservationConfirmation,name="confirmation"),
    path("essai/",courseViews.vue_historique,name="essaie"),
    path("course/mycourses/<str:idue>/<int:idpersonne>",courseViews.reservation_subject_student,name="subject_student"),
    path("course/mycourses/reservation-sujet/<str:idue>/<int:idsujet>",courseViews.confirmer_reservation_sujet,name='confirmation_reservation_student'), 
    path("sujet/etapes/",courseViews.etape_view, name="etapes"),
    path("inscription/",views.subscription,name="inscription"),

]
