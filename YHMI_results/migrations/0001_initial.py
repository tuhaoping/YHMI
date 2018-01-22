# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2018-01-22 07:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='YhmiEnrichment',
            fields=[
                ('feature', models.CharField(db_column='Feature', max_length=50, primary_key=True, serialize=False)),
                ('pro_en', models.TextField(blank=True, db_column='Pro_en', null=True)),
                ('pro_de', models.TextField(blank=True, db_column='Pro_de', null=True)),
                ('cod_en', models.TextField(blank=True, db_column='Cod_en', null=True)),
                ('cod_de', models.TextField(blank=True, db_column='Cod_de', null=True)),
            ],
            options={
                'db_table': 'yhmi_enrichment',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='YhmiEnrichmentTf',
            fields=[
                ('feature', models.CharField(db_column='Feature', max_length=50, primary_key=True, serialize=False)),
                ('pro', models.TextField(blank=True, db_column='Pro', null=True)),
                ('cod', models.TextField(blank=True, db_column='Cod', null=True)),
            ],
            options={
                'db_table': 'yhmi_enrichment_tf',
                'managed': False,
            },
        ),
    ]
