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


# Function to validate file extension
def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.png', '.xlsx', '.xls', '.zip']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


# fonction pour valider l'email
def validate_email(value):
    import re
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', value):
        raise ValidationError(u'Invalid email address.')


def validate_block(value):
    if value < 1 or value > 6:
        raise ValidationError(u'Invalid block number.')


# fonction pour définir le chemin de dépôt des fichiers pour un délivrable
def get_upload_path(instance, filename):
    # Récupérer le nom de la personne
    nom_personne = instance.nom_personne
    # Récupérer le nom du cours
    nom_cours = instance.nom_cours
    # Récupérer le numéro de la période
    num_periode = instance.annee_periode
    # Construire le chemin de dépôt
    return f'delivrables/{nom_personne}/{nom_cours}/{num_periode}/{filename}'


# models
class Cours(models.Model):
    idcours = models.AutoField(primary_key=True)
    idue = models.ForeignKey('Ue', models.DO_NOTHING, db_column='idue')
    nom = models.TextField(db_column='nom')
    idetudiant = models.ForeignKey('Etudiant',models.DO_NOTHING,db_column='idetudiant')

    class Meta:
        managed = False
        db_table = 'cours'


class Etudiant(models.Model):
    idetudiant = models.AutoField(primary_key=True, db_column='idetudiant')
    bloc = models.IntegerField(db_column='bloc', validators=[validate_block])
    idpersonne = models.ForeignKey('Personne', models.DO_NOTHING, db_column='idpersonne')
    idsujet = models.ForeignKey('Sujet', models.DO_NOTHING, db_column='idsujet')

    class Meta:
        managed = False
        db_table = 'etudiant'


class Inscription(models.Model):
    idinscription = models.AutoField(primary_key=True)
    idetudiant = models.ForeignKey(Etudiant, models.DO_NOTHING, db_column='idetudiant')
    idcours = models.ForeignKey(Cours, models.DO_NOTHING, db_column='idcours')

    class Meta:
        managed = False
        db_table = 'inscription'


class Periode(models.Model):
    idperiode = models.AutoField(primary_key=True, db_column='idperiode')
    annee = models.IntegerField(db_column='annee')

    class Meta:
        managed = False
        db_table = 'periode'


class Delivrable(models.Model):
    idDelivrable = models.AutoField(primary_key=True, db_column='iddelivrable')
    fichier = models.FileField(db_column='fichier', upload_to=get_upload_path, blank=True, null=True)
    typeFichier = models.TextField(db_column='typefichier', validators=[validate_file_extension])

    nom_personne: str
    nom_cours: str
    annee_periode: int

    def set_nom_personne(self, nom_personne):
        self.nom_personne = nom_personne

    def set_nom_cours(self, nom_cours):
        self.nom_cours = nom_cours

    def set_annee_periode(self, annee_periode):
        self.annee_periode = annee_periode


class Etape(models.Model):
    idEtape = models.AutoField(primary_key=True, db_column='idetape')
    delai = models.DateTimeField(db_column='delai')
    description = models.TextField(db_column='description')
    idPeriode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')
    idDelivrable = models.ForeignKey('Delivrable', models.DO_NOTHING, db_column='iddelivrable')


class PersonneManager(BaseUserManager):
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
    idpersonne = models.AutoField(primary_key=True, db_column='idpersonne')
    nom = models.TextField(db_column='nom')
    prenom = models.TextField(db_column='prenom')
    mail = models.TextField(unique=True, db_column='mail', validators=[validate_email])
    password = models.TextField(db_column='password')
    role = models.JSONField(db_column='role',default=list, blank=True, null=True)
    is_active = models.BooleanField(default=True, db_column='is_active'),
    is_staff = models.BooleanField(default=False, db_column='is_staff'),
    last_login = models.DateTimeField(null=True, blank=True, db_column='last_login')  # Ajoutez ce champ
    is_superuser = models.BooleanField(default=False, db_column='is_superuser')

    objects = PersonneManager()

    USERNAME_FIELD = 'mail'
    PASSWORD_FIELD = 'password'

    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'personne'


class Professeur(models.Model):
    idprof = models.AutoField(primary_key=True, db_column='idprof')
    specialite = models.TextField(db_column='specialite')
    idpersonne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idpersonne')
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')

    class Meta:
        managed = False
        db_table = 'professeur'


class Sujet(models.Model):
    idsujet = models.AutoField(primary_key=True, db_column='idsujet')
    titre = models.TextField(db_column='titre')
    descriptif = models.TextField(db_column='descriptif')
    destination = models.TextField(db_column='destination')
    estPris = models.BooleanField(db_column='estpris',default=False)
    fichier = models.FileField(upload_to='sujets/', blank=True, null=True, db_column='fichier',
                               validators=[validate_file_extension])
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode', default=1)
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof', default=1)
    idCours = models.ForeignKey(Cours, models.DO_NOTHING, db_column='idcours', default=1)

    class Meta:
        managed = False
        db_table = 'sujet'


class Ue(models.Model):
    idue = models.TextField(primary_key=True, db_column='idue')
    nom = models.TextField(db_column='nom')
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof')

    class Meta:
        managed = False
        db_table = 'ue'
