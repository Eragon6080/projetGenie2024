# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.core.files.storage import FileSystemStorage
from django.db import models


class Cours(models.Model):
    idcours = models.AutoField(primary_key=True)
    idue = models.ForeignKey('Ue', models.DO_NOTHING, db_column='idue')
    nom = models.TextField()

    class Meta:
        managed = False
        db_table = 'cours'


class Etudiant(models.Model):
    idetudiant = models.AutoField(primary_key=True)
    bloc = models.IntegerField()
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
    idperiode = models.AutoField(primary_key=True)
    annee = models.IntegerField()
    delaipremierepartie = models.DateField()
    delaideuxiemepartie = models.DateField()
    delaitroisiemepartie = models.DateField()
    delaifinal = models.DateField()

    class Meta:
        managed = False
        db_table = 'periode'


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
    idpersonne = models.AutoField(primary_key=True)
    nom = models.TextField()
    prenom = models.TextField()
    mail = models.TextField(unique=True,db_column='mail')
    password = models.TextField(db_column='password')
    role = models.TextField(db_column='role')
    is_active = models.BooleanField(default=True,db_column='is_active'),
    is_staff = models.BooleanField(default=False,db_column='is_staff'),
    last_login = models.DateTimeField(null=True, blank=True,db_column='last_login')  # Ajoutez ce champ
    is_superuser = models.BooleanField(default=False,db_column='is_superuser')

    objects = PersonneManager()

    USERNAME_FIELD = 'mail'
    PASSWORD_FIELD = 'password'

    REQUIRED_FIELDS = []

    class Meta:
        managed = False
        db_table = 'personne'


class Professeur(models.Model):
    idprof = models.AutoField(primary_key=True)
    specialite = models.TextField()
    idpersonne = models.ForeignKey(Personne, models.DO_NOTHING, db_column='idpersonne')
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')

    class Meta:
        managed = False
        db_table = 'professeur'


class Sujet(models.Model):
    idsujet = models.AutoField(primary_key=True)
    titre = models.TextField(db_column='titre')
    descriptif = models.TextField(db_column='descriptif')
    destination = models.TextField(db_column='destination')
    fichier = models.FileField(upload_to='sujets/',blank=True, null=True,db_column='fichier')
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode',default=1)
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof',default=1)

    class Meta:
        managed = False
        db_table = 'sujet'


class Ue(models.Model):
    idue = models.TextField(primary_key=True)
    nom = models.TextField()
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof')

    class Meta:
        managed = False
        db_table = 'ue'
