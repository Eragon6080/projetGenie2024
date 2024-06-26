# Generated by Django 5.0.3 on 2024-04-18 14:37

import polls.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_alter_delivrable_table_alter_etape_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichierDelivrable',
            fields=[
                ('idfichier', models.AutoField(db_column='idfichier', primary_key=True, serialize=False)),
                ('fichier', models.FileField(blank=True, db_column='fichier', null=True, upload_to=polls.models.get_upload_path)),
                ('rendu', models.BooleanField(db_column='rendu', default=False)),
            ],
            options={
                'db_table': 'fichierdelivrable',
                'managed': False,
            },
        ),
    ]
