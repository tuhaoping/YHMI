from django.db import models

# Create your models here.
class ConstInfoContact(models.Model):
    name = models.CharField(db_column='Name', max_length=100)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50)  # Field name made lowercase.
    work = models.CharField(db_column='Work', max_length=100, blank=True, null=True)  # Field name made lowercase.
    mail = models.CharField(db_column='Mail', max_length=50)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=100, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'const_info_contact'