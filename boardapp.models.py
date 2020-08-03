# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Schoolusers(models.Model):
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    school = models.ForeignKey('Schools', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'schoolusers'
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Schoolusers(models.Model):
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)
    school = models.ForeignKey('Schools', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'schoolusers'
