# Generated by Django 5.0.3 on 2024-03-30 15:20

import django.db.models.deletion
import polls.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivrable',
            fields=[
                ('idDelivrable', models.AutoField(primary_key=True, serialize=False)),
                ('fichier', models.FileField(blank=True, db_column='fichier', null=True, upload_to=polls.models.get_upload_path)),
                ('typeFichier', models.TextField(db_column='typeFichier', validators=[polls.models.validate_file_extension])),
            ],
        ),
        migrations.CreateModel(
            name='Etape',
            fields=[
                ('idEtape', models.AutoField(primary_key=True, serialize=False)),
                ('delai', models.DateTimeField(db_column='delai')),
                ('description', models.TextField(db_column='description')),
                ('idDelivrable', models.ForeignKey(db_column='idDelivrable', on_delete=django.db.models.deletion.DO_NOTHING, to='polls.delivrable')),
                ('idPeriode', models.ForeignKey(db_column='idPeriode', on_delete=django.db.models.deletion.DO_NOTHING, to='polls.periode')),
            ],
        ),
    ]
