# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
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


class Personne(models.Model):
    idpersonne = models.AutoField(primary_key=True)
    nom = models.TextField()
    prenom = models.TextField()
    mail = models.TextField(unique=True)
    motdepasse = models.TextField()
    rolepersonne = models.TextField()

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
    idsujet = models.AutoField(primary_key=True,db_column='idsujet')
    titre = models.TextField()
    descriptif = models.TextField()
    fichier = models.BinaryField(blank=True, null=True)
    idperiode = models.ForeignKey(Periode, models.DO_NOTHING, db_column='idperiode')
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof')

    class Meta:
        managed = False
        db_table = 'sujet'


class Ue(models.Model):
    idue = models.AutoField(primary_key=True)
    nom = models.TextField()
    idprof = models.ForeignKey(Professeur, models.DO_NOTHING, db_column='idprof')

    class Meta:
        managed = False
        db_table = 'ue'
