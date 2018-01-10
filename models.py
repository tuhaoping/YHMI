# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class YhmiEnrichment(models.Model):
    feature = models.CharField(db_column='Feature', primary_key=True, max_length=50)  # Field name made lowercase.
    pro_en = models.TextField(db_column='Pro_en', blank=True, null=True)  # Field name made lowercase.
    pro_de = models.TextField(db_column='Pro_de', blank=True, null=True)  # Field name made lowercase.
    cod_en = models.TextField(db_column='Cod_en', blank=True, null=True)  # Field name made lowercase.
    cod_de = models.TextField(db_column='Cod_de', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'yhmi_enrichment'
