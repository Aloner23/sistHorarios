# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Materias(models.Model):
    clave = models.CharField(db_column='Clave', primary_key=True, max_length=45)  # Field name made lowercase.
    nombre = models.CharField(max_length=45, blank=True, null=True)
    horas = models.IntegerField(blank=True, null=True)
    semestre = models.IntegerField(blank=True, null=True)
    periodo = models.CharField(max_length=45, blank=True, null=True)
    carrera = models.CharField(max_length=45, blank=True, null=True)
    tipo = models.CharField(max_length=45, blank=True, null=True)
    preferencia = models.CharField(max_length=45, blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'materias'


class Profesores(models.Model):
    idprof = models.AutoField(db_column='idProf', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45, blank=True, null=True)
    horario = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profesores'


class ProfesoresHasMaterias(models.Model):
    profesores_idprof = models.OneToOneField(Profesores, models.DO_NOTHING, db_column='Profesores_idProf', primary_key=True)  # Field name made lowercase.
    materias_clave = models.ForeignKey(Materias, models.DO_NOTHING, db_column='Materias_Clave')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'profesores_has_materias'
        unique_together = (('profesores_idprof', 'materias_clave'),)


class Salones(models.Model):
    salon = models.CharField(primary_key=True, max_length=45)
    tipo = models.CharField(max_length=45, blank=True, null=True)
    lun = models.CharField(max_length=45, blank=True, null=True)
    mar = models.CharField(max_length=45, blank=True, null=True)
    mier = models.CharField(max_length=45, blank=True, null=True)
    jue = models.CharField(max_length=45, blank=True, null=True)
    vie = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salones'

"""
class SalonesHasProfesoresHasMaterias(models.Model):
    salones_salon = models.OneToOneField(Salones, models.DO_NOTHING, db_column='Salones_salon', primary_key=True)  # Field name made lowercase.
    profesores_idprof = models.ForeignKey(ProfesoresHasMaterias, models.DO_NOTHING, db_column='Profesores_idProf')  # Field name made lowercase.
    materias_clave = models.ForeignKey(ProfesoresHasMaterias, models.DO_NOTHING, db_column='Materias_Clave', to_field='Materias_Clave')  # Field name made lowercase.
    horario = models.CharField(max_length=45, blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salones_has_profesores_has_materias'
        unique_together = (('salones_salon', 'profesores_idprof', 'materias_clave'),)
"""
class SalonesHasProfesoresHasMaterias(models.Model):
    salones_salon = models.CharField(max_length=45, blank=True, null=True)
    profesores_idprof = models.IntegerField(blank=True, null=True)
    materias_clave =models.CharField(max_length=45, blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salones_has_profesores_has_materias'
        unique_together = (('salones_salon', 'profesores_idprof', 'materias_clave'),)