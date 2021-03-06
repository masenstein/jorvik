# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-05-10 18:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('anagrafica', '0040_refactor_nome_cognome'),
        ('curriculum', '0004_titoli_di_studio'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotiziaTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('testo', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='NotiziaTestSegmento',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('segmento', models.CharField(choices=[('A', 'Tutti gli utenti di Gaia'), ('B', 'Volontari'), ('C', 'Volontari da meno di un anno'), ('D', 'Volontari da più di un anno'), ('E', 'Volontari con meno di 35 anni'), ('F', 'Volontari con 35 anni o più'), ('G', 'Sostenitori CRI'), ('H', 'Aspiranti volontari iscritti a un corso'), ('I', 'Tutti i Presidenti'), ('J', 'Presidenti di Comitati Locali'), ('K', 'Presidenti di Comitati Regionali'), ('L', 'Delegati US'), ('M', 'Delegati Obiettivo I'), ('N', 'Delegati Obiettivo II'), ('O', 'Delegati Obiettivo III'), ('P', 'Delegati Obiettivo IV'), ('Q', 'Delegati Obiettivo V'), ('R', 'Delegati Obiettivo VI'), ('S', 'Referenti di un’Attività di Area I'), ('T', 'Referenti di un’Attività di Area II'), ('U', 'Referenti di un’Attività di Area III'), ('V', 'Referenti di un’Attività di Area IV'), ('W', 'Referenti di un’Attività di Area V'), ('X', 'Referenti di un’Attività di Area VI'), ('Y', 'Delegati Autoparco'), ('Z', 'Delegati Formazione'), ('AA', 'Volontari aventi un dato titolo')], max_length=256)),
                ('notiziatest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='segmenti', to='segmenti_test.NotiziaTest')),
                ('sede', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='anagrafica.Sede')),
                ('titolo', models.ForeignKey(blank=True, help_text="Usato solo con il segmento 'Volontari aventi un dato titolo'", null=True, on_delete=django.db.models.deletion.CASCADE, to='curriculum.Titolo')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
