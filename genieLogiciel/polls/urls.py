from django.urls import path
from . import views, courseViews, adminViews

urlpatterns = [
    # pages communes
    path("", views.login, name="login"),
    path("home/", views.accueil, name="accueil"),
    path("profile/", views.profile, name="profile"),
    path("logout/", views.logout, name="logout"),
    path("back/", courseViews.back, name="back"),

    # pages de cours pour un professeur, superviseur ou admin
    path("course/", views.home, name="home"),
    path("course/<str:idue>/", views.course, name="course"),
    path("course/<str:idue>/sujet/reservation", courseViews.reservation, name="reservation d'un sujet"),
    path("course/<str:idue>/sujet/reservation/<int:idsujet>", courseViews.booking, name="reservation d'un sujet"),
    path("course/<str:idue>/sujet/reservation/<int:idsujet>/confirmation", courseViews.validation_booking, name="confirmation"),
    path("course/<str:idue>/topics/", courseViews.topics, name="topics"),
    path("course/<str:idue>/mytopics/", courseViews.myTopics, name="myTopics"),
    path("course/<str:idue>/new/", courseViews.add_topic, name="addTopic"),
    path("course/<str:idue>/ReuseSubject/", courseViews.new, name="ReuseSubject"),
    path("course/<str:idue>/topics/<int:sujet_id>/note", courseViews.NoteTopic, name="NoteTopic"),
    path("course/<str:idue>/participants/", courseViews.participants, name="participants"),
    path("course/<str:idue>/timeline/", courseViews.etape_view, name="gestion timeline"),
    path("course/<str:idue>/timeline/delete/<int:idetape>", courseViews.deleteStep, name="deleteStep"),
    path("course/<str:idue>/timeline/select/step/<int:idetapeue>", courseViews.selectStep, name="selectStep"),
    path("course/<str:idue>/timeline/access/<str:val>", courseViews.changeAccess, name="active ou désactive la timeline d'une ue"),
    path("fiche/<int:idpersonne>", views.fiche, name="fiche"),
    
    # pages spécifiques aux admins 
    path("admin/", adminViews.admin, name="admin"),
    path("admin/role/", adminViews.role, name="role"),
    path("admin/role/<str:view>", adminViews.role, name="roleView"),
    path("admin/courses/", adminViews.courses, name="coursSummary"),
    path("sujet/history/", courseViews.vue_historique, name="vue_historique"),
    path("sujet/history/<int:annee>", courseViews.vue_historique_annee, name="vue_historaieAnnee"),



    # gestion des sujets
    path('sujet/edit/<int:sujet_id>/', courseViews.editTopic, name='edit_topic'),
    path('sujet/delete/<int:sujet_id>/', courseViews.deleteTopic, name='delete_topic'),
   
    

    # pages de cours pour un étudiant
    path("mycourses/", courseViews.mycourses, name="page d'acceuil des cours de l'etudiant"),
    path("mycourses/<str:idue>/", courseViews.mycourse, name="page d'un cours"),
    
    path("mycourses/<str:idue>/<int:idpersonne>", courseViews.reservation_subject_student, name="subject_student"),
    path("mycourses/<str:idue>/reservation-sujet/<int:idsujet>", courseViews.confirmer_reservation_sujet, name='confirmation_reservation_student'),

    # pages de gestion des inscriptions pour les étudiants
    path("inscription/", views.subscription, name="inscription"),
    path("course/inscription", courseViews.subscription, name="inscription"),
    path("course/inscription/<str:idue>/<str:nom>", courseViews.subscription_validation, name="inscription"),
    path("course/desincription", views.desinscription, name="desinscription"),
    path("course/desinscription/<int:idcours>", views.desinscription_validation, name="desinscription_validation"),
    path("course/desinscription/<str:idue>/<int:idpersonne>", views.desinscription_etudiant, name="desinscription d'un etudiant d'une ue"),
    

    # utils
    path("ok/", courseViews.ok, name="ok"),
    path("suivi/", views.yes, name="yes"),
    path("switch_role/<str:role>", views.switchRole, name="switch_role"),

    # deprecated
    path("course/<str:idue>/steps/", courseViews.afficher_etapes_ue, name="steps"),
    path("echeance/", views.echeance_and_upload, name="echeance_and_upload"),
    path("echeance/<int:delivrable_id>/<int:idcours>/<int:idperiode>", views.echeance_and_upload,
         name="echeance_and_upload"),
    

]
