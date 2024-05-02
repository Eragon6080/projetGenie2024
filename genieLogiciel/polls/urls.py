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
    path("course/<str:idue>/topics/", courseViews.topics, name="topics"),
    path("course/<str:idue>/mytopics/", courseViews.myTopics, name="myTopics"),
    path("course/<str:idue>/new/", courseViews.add_topic, name="addTopic"),
    path("course/<str:idue>/ReuseSubject/", courseViews.new, name="ReuseSubject"),
    path("course/<str:idue>/participants/", courseViews.participants, name="participants"),
    path("course/<str:idue>/timeline/", courseViews.etape_view, name="gestion timeline"),
    path("course/<str:idue>/timeline/delete/<int:idetape>", courseViews.deleteStep, name="deleteStep"),
    path("course/<str:idue>/timeline/select/step/<int:idetapeue>", courseViews.selectStep, name="selectStep"),
    path("fiche/<int:idpersonne>", views.fiche, name="fiche"),
    
    # pages spécifiques aux admins 
    path("admin/", adminViews.admin, name="admin"),
    path("admin/role/", adminViews.role, name="role"),
    path("admin/role/<str:view>", adminViews.role, name="roleView"),
    path("admin/courses/", adminViews.courses, name="coursSummary"),

   
    
    
    path('sujet/edit/<int:sujet_id>/', courseViews.editTopic, name='edit_topic'),
    path('sujet/delete/<int:sujet_id>/', courseViews.deleteTopic, name='delete_topic'),
    path("course/<str:idue>/steps/", courseViews.afficher_etapes_ue, name="steps"),
    

    # pages de cours pour un étudiant
    path("mycourses/", courseViews.mycourses, name="page d'acceuil des cours de l'etudiant"),
    path("mycourses/<str:idue>/", courseViews.mycourse, name="page d'un cours"),
    
    path("mycourses/<str:idue>/<int:idpersonne>", courseViews.reservation_subject_student, name="subject_student"),
    path("mycourses/reservation-sujet/<str:idue>/<int:idsujet>", courseViews.confirmer_reservation_sujet, name='confirmation_reservation_student'),

    # pages de gestion des inscriptions pour les étudiants
    path("inscription/", views.subscription, name="inscription"),
    path("course/inscription", courseViews.subscription, name="inscription"),
    path("course/inscription/<str:idue>/<str:nom>", courseViews.subscription_validation, name="inscription"),
    path("course/desincription", views.desinscription, name="desinscription"),
    path("course/desincription/<int:idcours>", views.desinscriptionValidation, name="desinscriptionValidation"),
    path("course/desinscription/<str:idue>/<int:idpersonne>", views.desinscriptionEtudiant, name="desinscription d'un etudiant d'une ue"),
    

    # utils
    path("ok/", courseViews.ok, name="ok"),
    path("suivi/", views.yes, name="yes"),
    path("switch_role/<str:role>", views.switchRole, name="switch_role"),

    path("echeance/", views.echeance_and_upload, name="echeance_and_upload"),
    path("echeance/<int:delivrable_id>/<int:idcours>/<int:idperiode>", views.echeance_and_upload,
         name="echeance_and_upload"),
    path("sujet/reservation", courseViews.reservation, name="reservation"),
    path("sujet/reservation/<int:idsujet>", courseViews.booking, name="reservation"),
    path("sujet/reservation/confirmation/<int:idsujet>", courseViews.validation_booking, name="confirmation"),
    path("essai/", courseViews.vue_historique, name="essaie"),
    
    
    

]
