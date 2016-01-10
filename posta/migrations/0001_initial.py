# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import social.models


class Migration(migrations.Migration):

    dependencies = [
        ('anagrafica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Destinatario',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('inviato', models.BooleanField(default=False)),
                ('tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('errore', models.CharField(blank=True, max_length=256, default=None, null=True)),
            ],
            options={
                'verbose_name': 'Destinatario di posta',
                'verbose_name_plural': 'Destinatario di posta',
            },
        ),
        migrations.CreateModel(
            name='Messaggio',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('creazione', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ultima_modifica', models.DateTimeField(auto_now=True, db_index=True)),
                ('oggetto', models.CharField(max_length=128, default='(Nessun oggetto)', db_index=True)),
                ('corpo', models.TextField(blank=True, default='(Nessun corpo)')),
                ('ultimo_tentativo', models.DateTimeField(blank=True, default=None, null=True)),
                ('terminato', models.DateTimeField(blank=True, default=None, null=True)),
                ('mittente', models.ForeignKey(to='anagrafica.Persona', null=True, default=None, blank=True)),
            ],
            options={
                'verbose_name': 'Messaggio di posta',
                'verbose_name_plural': 'Messaggi di posta',
            },
            bases=(social.models.ConGiudizio, models.Model),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='messaggio',
            field=models.ForeignKey(related_name='oggetti_destinatario', blank=True, to='posta.Messaggio'),
        ),
        migrations.AddField(
            model_name='destinatario',
            name='persona',
            field=models.ForeignKey(to='anagrafica.Persona', null=True, default=None, blank=True),
        ),
    ]