# Generated by Django 5.0.3 on 2024-03-24 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='personne',
            fields=[
                ('idpersonne', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.TextField()),
                ('prenom', models.TextField()),
                ('mail', models.TextField(db_column='mail', unique=True)),
                ('password', models.TextField(db_column='password')),
                ('role', models.TextField(db_column='role')),
                ('last_login', models.DateTimeField(blank=True, db_column='last_login', null=True)),
                ('is_superuser', models.BooleanField(db_column='is_superuser', default=False)),
            ],
            options={
                'db_table': 'personne',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Cours',
            fields=[
                ('idcours', models.AutoField(primary_key=True, serialize=False)),
                ('nom', models.TextField()),
            ],
            options={
                'db_table': 'cours',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Etudiant',
            fields=[
                ('idetudiant', models.AutoField(primary_key=True, serialize=False)),
                ('bloc', models.IntegerField()),
            ],
            options={
                'db_table': 'etudiant',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Inscription',
            fields=[
                ('idinscription', models.AutoField(primary_key=True, serialize=False)),
            ],
            options={
                'db_table': 'inscription',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Periode',
            fields=[
                ('idperiode', models.AutoField(primary_key=True, serialize=False)),
                ('annee', models.IntegerField()),
                ('delaipremierepartie', models.DateField()),
                ('delaideuxiemepartie', models.DateField()),
                ('delaitroisiemepartie', models.DateField()),
                ('delaifinal', models.DateField()),
            ],
            options={
                'db_table': 'periode',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Professeur',
            fields=[
                ('idprof', models.AutoField(primary_key=True, serialize=False)),
                ('specialite', models.TextField()),
            ],
            options={
                'db_table': 'professeur',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Sujet',
            fields=[
                ('idsujet', models.AutoField(primary_key=True, serialize=False)),
                ('titre', models.TextField()),
                ('descriptif', models.TextField()),
                ('fichier', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'sujet',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ue',
            fields=[
                ('idue', models.TextField(primary_key=True, serialize=False)),
                ('nom', models.TextField()),
            ],
            options={
                'db_table': 'ue',
                'managed': False,
            },
        ),
    ]
