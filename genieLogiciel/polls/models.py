# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.db import models

"""
Ce fichier contient les différentes classes représentant les tables de la base de données. Cela permet une gestion
des différentes opérations CRUD sur les tables de la base de données grâce à l'ORM de Django.
"""


# Function to validate file extension
def validate_file_extension(value: str):
    """
    La fonction dit si le fichier contient une extension correct
    :param value: Le nom du fichier
    :return: Le fichier si celui-ci contient un nom d'extension correct
    """
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions: list[str] = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls', '.zip']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'L\' extension du fichier n\'est pas supporté.')


# fonction pour valider l'email
def validate_email(value: str):
    """
    Fonction regardant si l'adresse mail est valide ou non
    :param value: une adresse mail
    :return: une exception si le mail n'est pas valide
    """
    import re
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
        raise ValidationError(u'L\'adresse mail n\'est pas valide.')


def validate_block(value: int):
    """
    Regarde si le numéro de bloc est valide
    :param value:
    :return: le numéro d'un block
    """
    if value < 1 or value > 6:
        raise ValidationError(u'Invalid block number.')


# fonction pour définir le chemin de dépôt des fichiers pour un délivrable
def get_upload_path(instance, filename: str):
    """
    Donne le nom complet de l'adresse du fichier dans django
    :param instance:
    :param filename: le nom du fichier
    :return:
    """
    # Récupérer le nom de la personne
    nom_personne: str = instance.nom_personne
    # Récupérer le nom du cours
    nom_cours: str = instance.nom_cours
    # Récupérer le numéro de la période
    num_periode: int = instance.annee_periode
    # Construire le chemin de dépôt
    return f'delivrables/{nom_personne}/{nom_cours}/{num_periode}/{filename}'


# models
class Cours(models.Model):
    """
    Représentation de la table cours en BD
    """
    idcours = models.AutoField(primary_key=True)
    idue = models.ForeignKey('Ue', models.DO_NOTHING, db_column='idue')
    nom = models.TextField(db_column='nom')
    idetudiant = models.ForeignKey('Etudiant', models.DO_NOTHING, db_column='idetudiant')

    class Meta:
        managed: bool = False
        db_table: str = 'cours'


class Etudiant(models.Model):
    """
    Représentation en python de la table étudiant de la base de données.
    """
    idetudiant = models.AutoField(primary_key=True, db_column='idetudiant')
    bloc = models.IntegerField(db_column='bloc', validators=[validate_block])
    idpersonne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idpersonne')

    class Meta:
        managed: bool = False
        db_table: str = 'etudiant'


class Periode(models.Model):
    """
    Représentation de la table période de la base de données
    """
    idperiode = models.AutoField(primary_key=True, db_column='idperiode')
    annee = models.IntegerField(db_column='annee')

    class Meta:
        managed: bool = False
        db_table: str = 'periode'


class Delivrable(models.Model):
    """
    Représentation d'un délivrable dans la base de données
    Un délivrable est ici un devoir à rendre. Le type de fichier correspond à l'extension du fichier accepté en BD
    """
    iddelivrable = models.AutoField(primary_key=True, db_column='iddelivrable')
    typeFichier = models.TextField(db_column='typefichier', validators=[validate_file_extension])

    class Meta:
        managed: bool = False
        db_table: str = 'delivrable'


class Etape(models.Model):
    """
    Classe représentant la table Etape de la base de données
    """
    idetape = models.AutoField(primary_key=True, db_column='idetape')
    datedebut = models.DateTimeField(db_column='datedebut')
    datefin = models.DateTimeField(db_column='datefin')
    titre = models.TextField(db_column='titre')
    description = models.TextField(db_column='description')
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')
    iddelivrable = models.ForeignKey(Delivrable, models.DO_NOTHING, db_column='iddelivrable')

    class Meta:
        managed: bool = False
        db_table: str = 'etape'


class PersonneManager(BaseUserManager):
    """
    Une classe représentant un moyen d'incorporer une classe avec l'authentification propre à django. Elle est ici liée
    à la table personne de la base de données.
    """

    def create_user(self, mail, password=None, **extra_fields):
        if not mail:
            raise ValueError('The Email field must be set')
        mail = self.normalize_email(mail)
        user = self.model(mail=mail, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Personne(AbstractBaseUser, PermissionsMixin):
    """
    Représentation de la table personne en BD
    Cette table est mélangée avec le système d'authentification de django
    """
    idpersonne = models.AutoField(primary_key=True, db_column='idpersonne')
    nom = models.TextField(db_column='nom')
    prenom = models.TextField(db_column='prenom')
    mail = models.TextField(unique=True, db_column='mail', validators=[validate_email])
    password = models.TextField(db_column='password')
    role = models.JSONField(db_column='role', default=list, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_column='is_active'),
    is_staff = models.BooleanField(default=False, db_column='is_staff'),
    last_login = models.DateTimeField(null=True, blank=True, db_column='last_login')  # Ajoutez ce champ
    is_superuser = models.BooleanField(default=False, db_column='is_superuser')

    objects = PersonneManager()

    USERNAME_FIELD = 'mail'
    PASSWORD_FIELD = 'password'

    REQUIRED_FIELDS: list[str] = []

    class Meta:
        managed: bool = False
        db_table: str = 'personne'


class Professeur(models.Model):
    """
    Classe représentant la table Professeur en base de données.
    """
    idprof = models.AutoField(primary_key=True, db_column='idprof')
    specialite = models.TextField(db_column='specialite')
    idpersonne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idpersonne')
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')

    class Meta:
        managed: bool = False
        db_table: str = 'professeur'


class Sujet(models.Model):
    """
    Classe représentant la table sujet de la base de données
    """
    idsujet = models.AutoField(primary_key=True, db_column='idsujet')
    titre = models.TextField(db_column='titre')
    descriptif = models.TextField(db_column='descriptif')
    destination = models.TextField(db_column='destination')
    estpris = models.BooleanField(db_column='estreserve', default=False)
    fichier = models.FileField(upload_to='sujets/', blank=True, null=True, db_column='fichier',
                               validators=[validate_file_extension])
    mark = models.IntegerField(db_column='mark', default=0)
    nbpersonnes = models.IntegerField(db_column='nbpersonnes', default=1, )
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode', default=1)
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprofesseur')
    idsuperviseur = models.ForeignKey('Superviseur', models.DO_NOTHING, db_column='idsuperviseur')
    idue = models.ForeignKey('Ue', models.DO_NOTHING, db_column='idue')

    class Meta:
        managed: bool = False
        db_table: str = 'sujet'


class Ue(models.Model):
    """
    Classe représentant une ue, un cours dans l'enseignement supérieur de Belgique
    """
    idue = models.TextField(primary_key=True, db_column='idue')
    nom = models.TextField(db_column='nom', default="Matthys")
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof')
    isopen = models.BooleanField(db_column='isopen', default=False)

    class Meta:
        managed: bool = False
        db_table: str = 'ue'


class EtapeUe(models.Model):
    """
    Représentation de la table étape ue de la base de données. Elle permet
    de savoir dans quelle étape pour l'ue, on se trouve en BD.
    """
    idetapeue = models.AutoField(primary_key=True, db_column='idetapeue')
    idue = models.ForeignKey(Ue, models.DO_NOTHING, db_column='idue')
    idetape = models.ForeignKey(Etape, models.DO_NOTHING, db_column='idetape')
    etapecourante = models.BooleanField(db_column='etapecourante', default=False)

    class Meta:
        managed: bool = False
        db_table: str = 'etapeue'


class FichierDelivrable(models.Model):
    """
    Classe représentant une tâche, un délivrable rendu
    """
    idfichier = models.AutoField(primary_key=True, db_column='idfichier')
    fichier = models.FileField(db_column='fichier', upload_to=get_upload_path, blank=True, null=True)
    rendu = models.BooleanField(db_column='estrendu', default=False)  # Champ pour marquer si le délivrable a été rendu
    idetudiant = models.ForeignKey(Etudiant, models.DO_NOTHING, db_column='idetudiant')
    iddelivrable = models.ForeignKey(Delivrable, models.DO_NOTHING, db_column='iddelivrable')
    note = models.IntegerField(db_column='note', null=True)
    estconfidentiel = models.BooleanField(db_column='estconfidentiel', default=False)
    idsujet = models.ForeignKey(Sujet, models.DO_NOTHING, db_column='idsujet')

    nom_personne: str
    nom_cours: str
    annee_periode: int

    def set_nom_personne(self, nom_personne: str):
        self.nom_personne = nom_personne

    def set_nom_cours(self, nom_cours: str):
        self.nom_cours = nom_cours

    def set_annee_periode(self, annee_periode: int):
        self.annee_periode = annee_periode

    class Meta:
        managed = False
        db_table = 'fichierdelivrable'


class Superviseur(models.Model):
    """
    Représentation de la table superviseur de la base de données. Un superviseur est un professeur qui supervise un sujet.
    Contrairement au professeur classque, le superviseur a une vue limitée sur un cours (ici, ue).
    """
    idsuperviseur = models.AutoField(primary_key=True, db_column='idsuperviseur')
    specialite = models.TextField(db_column='specialite', blank=False)
    idpersonne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idpersonne')

    class Meta:
        managed: bool = False
        db_table: str = 'superviseur'


class Supervision(models.Model):
    """
    Représentation de la table supervision de la base de données. Elle permet de savoir quel superviseur supervise quelle ue.
    """
    idsupervision = models.AutoField(primary_key=True, db_column='idsupervision')
    description = models.TextField(db_column='description', blank=False)
    idsuperviseur = models.ForeignKey(Superviseur, models.DO_NOTHING, db_column='idsuperviseur')
    idue = models.ForeignKey(Ue, models.DO_NOTHING, db_column='idue')

    class Meta:
        managed:bool = False
        db_table:str = 'supervision'


class SelectionSujet(models.Model):
    """
    Représentation de la table selection sujet de la base de données. Elle permet de savoir quel étudiant a sélectionné quel sujet.
    """
    idselection = models.AutoField(primary_key=True, db_column='idselection')
    idetudiant = models.ForeignKey(Etudiant, models.DO_NOTHING, db_column='idetudiant')
    idsujet = models.ForeignKey(Sujet, models.DO_NOTHING, db_column='idsujet')
    is_involved = models.BooleanField(db_column='is_involved', default=False)

    class Meta:
        managed:bool = False
        db_table:str = 'selectionsujet'
