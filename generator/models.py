from django.db import models

# Create your models here.

class Profesores(models.Model):
    idprof = models.AutoField(db_column='idProf', primary_key=True)  # Field name made lowercase.
    nombre = models.CharField(max_length=45, blank=True, null=True)
    horario = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'profesores'

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
class ProfesoresHasMaterias(models.Model):
    profesores_idprof = models.OneToOneField(Profesores, models.DO_NOTHING, db_column='Profesores_idProf', primary_key=True)  # Field name made lowercase.
    materias_clave = models.ForeignKey(Materias, models.DO_NOTHING, db_column='Materias_Clave')  # Field name made lowercase.
    #materias_clave= models.CharField(max_length=45, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'profesores_has_materias'
        unique_together = (('profesores_idprof', 'materias_clave'),)


class SalonesHasProfesoresHasMaterias(models.Model):
    salones_salon = models.OneToOneField(Salones, models.DO_NOTHING, db_column='Salones_salon', primary_key=True)  # Field name made lowercase.
    profesores_idprof = models.OneToOneField(Profesores, models.DO_NOTHING, db_column='Profesores_idProf')  # Field name made lowercase.
    materias_clave = models.ForeignKey(Materias, models.DO_NOTHING, db_column='Materias_Clave')  # Field name made lowercase.

    horario = models.CharField(max_length=45, blank=True, null=True)
    dias = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'salones_has_profesores_has_materias'
        unique_together = (('salones_salon', 'profesores_idprof', 'materias_clave'),)
