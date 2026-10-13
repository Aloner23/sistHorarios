"""Modelos del generador de horarios.

Los nombres de tabla (``db_table``) conservan el esquema MySQL original del
proyecto (``profesores``, ``materias``, ``salones``, ``profesores_has_materias``
y ``salones_has_profesores_has_materias``).
"""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from . import scheduler


class TipoSalon(models.TextChoices):
    BUTACA = "Butaca", "Butacas"
    COMPUTADORA = "Computadora", "Computadoras"
    LABORATORIO = "Laboratorio", "Laboratorio"


class Turno(models.TextChoices):
    MANANA = "Manana", "Mañana"
    TARDE = "Tarde", "Tarde"
    NOCHE = "Noche", "Noche"


class Dias(models.TextChoices):
    """Días en que se imparte una clase.

    En el diseño original sólo existían ``1`` (Lun/Mié) y ``2`` (Mar/Jue);
    se agregan los días sueltos para materias de una sola sesión semanal.
    """

    LUN_MIE = "LM", "Lunes y miércoles"
    MAR_JUE = "MJ", "Martes y jueves"
    LUN = "L", "Lunes"
    MAR = "M", "Martes"
    MIE = "X", "Miércoles"
    JUE = "J", "Jueves"
    VIE = "V", "Viernes"


disponibilidad_validator = RegexValidator(
    regex=r"^((\d{1,2}-\d{1,2}|x),){3}$",
    message="Formato esperado: 'inicio-fin,' por bloque (mañana, tarde, noche), "
    "o 'x,' para un bloque cerrado. Ej.: 0-10,11-20,21-30,",
)


class Profesor(models.Model):
    id = models.AutoField(db_column="idProf", primary_key=True)
    nombre = models.CharField(max_length=80)
    correo = models.EmailField(blank=True)
    horario = models.CharField(
        "dedicación",
        max_length=45,
        blank=True,
        help_text="Tipo de contratación, p. ej. Tiempo completo o Asignatura.",
    )
    materias = models.ManyToManyField(
        "Materia", through="ProfesorMateria", related_name="profesores", blank=True
    )

    class Meta:
        db_table = "profesores"
        ordering = ["nombre"]
        verbose_name = "profesor"
        verbose_name_plural = "profesores"

    def __str__(self) -> str:
        return self.nombre


class Materia(models.Model):
    clave = models.CharField(db_column="Clave", primary_key=True, max_length=20)
    nombre = models.CharField(max_length=80)
    horas = models.PositiveSmallIntegerField(
        help_text="Horas por semana.", validators=[MinValueValidator(1), MaxValueValidator(20)]
    )
    semestre = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    periodo = models.CharField(max_length=45, blank=True)
    carrera = models.CharField(max_length=60)
    tipo = models.CharField(
        "tipo de salón", max_length=20, choices=TipoSalon.choices, default=TipoSalon.BUTACA
    )
    preferencia = models.CharField(
        "turno preferido", max_length=10, choices=Turno.choices, default=Turno.MANANA
    )
    dias = models.PositiveSmallIntegerField(
        "sesiones por semana",
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(2)],
        help_text="2 = dos sesiones (Lun/Mié o Mar/Jue); 1 = una sola sesión.",
    )

    class Meta:
        db_table = "materias"
        ordering = ["carrera", "semestre", "clave"]

    def __str__(self) -> str:
        return f"{self.clave} · {self.nombre}"

    @property
    def medias_horas_por_sesion(self) -> int:
        return scheduler.medias_horas_por_sesion(self.horas, self.dias)


class Salon(models.Model):
    clave = models.CharField(db_column="salon", primary_key=True, max_length=45)
    tipo = models.CharField(max_length=20, choices=TipoSalon.choices, default=TipoSalon.BUTACA)
    lun = models.CharField(
        max_length=45, default=scheduler.JORNADA_COMPLETA, validators=[disponibilidad_validator]
    )
    mar = models.CharField(
        max_length=45, default=scheduler.JORNADA_COMPLETA, validators=[disponibilidad_validator]
    )
    mier = models.CharField(
        max_length=45, default=scheduler.JORNADA_COMPLETA, validators=[disponibilidad_validator]
    )
    jue = models.CharField(
        max_length=45, default=scheduler.JORNADA_COMPLETA, validators=[disponibilidad_validator]
    )
    vie = models.CharField(
        max_length=45, default=scheduler.JORNADA_COMPLETA, validators=[disponibilidad_validator]
    )

    class Meta:
        db_table = "salones"
        ordering = ["clave"]
        verbose_name = "salón"
        verbose_name_plural = "salones"

    def __str__(self) -> str:
        return self.clave

    @property
    def disponibilidad(self) -> list[str]:
        """Cadenas de disponibilidad de lunes a viernes."""
        return [self.lun, self.mar, self.mier, self.jue, self.vie]


class ProfesorMateria(models.Model):
    """Materia que imparte un profesor (antes ``ProfesoresHasMaterias``).

    El modelo original usaba un ``OneToOneField`` como llave primaria sobre el
    profesor, lo que en Django impedía que un profesor tuviera más de una
    materia. Ahora son dos llaves foráneas con una restricción de unicidad.
    """

    profesor = models.ForeignKey(
        Profesor, on_delete=models.CASCADE, db_column="Profesores_idProf", related_name="clases"
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, db_column="Materias_Clave", related_name="clases"
    )

    class Meta:
        db_table = "profesores_has_materias"
        ordering = ["materia__clave", "profesor__nombre"]
        constraints = [
            models.UniqueConstraint(fields=["profesor", "materia"], name="profesor_materia_unica")
        ]
        verbose_name = "materia de profesor"
        verbose_name_plural = "materias de profesores"

    def __str__(self) -> str:
        return f"{self.profesor} — {self.materia.clave}"

    @property
    def asignada(self) -> bool:
        return hasattr(self, "asignacion")


class Asignacion(models.Model):
    """Clase (profesor + materia) colocada en un salón, días y horario.

    Antes ``SalonesHasProfesoresHasMaterias``. El horario se guarda como
    índices de medias horas a partir de las 7:00 (``inicio`` inclusivo,
    ``fin`` exclusivo), igual que la notación ``"a-b"`` del algoritmo original.
    """

    clase = models.OneToOneField(
        ProfesorMateria, on_delete=models.CASCADE, related_name="asignacion"
    )
    salon = models.ForeignKey(
        Salon, on_delete=models.PROTECT, db_column="Salones_salon", related_name="asignaciones"
    )
    dias = models.CharField(max_length=2, choices=Dias.choices)
    inicio = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(scheduler.TOTAL_MEDIAS_HORAS - 1)]
    )
    fin = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(scheduler.TOTAL_MEDIAS_HORAS)]
    )

    class Meta:
        db_table = "salones_has_profesores_has_materias"
        ordering = ["clase__materia__clave"]
        verbose_name = "asignación"
        verbose_name_plural = "asignaciones"

    def __str__(self) -> str:
        return f"{self.clase} @ {self.salon} {self.get_dias_display()} {self.horario}"

    @property
    def horario(self) -> str:
        return f"{scheduler.etiqueta_hora(self.inicio)}–{scheduler.etiqueta_hora(self.fin)}"

    @property
    def dias_indices(self) -> tuple[int, ...]:
        return scheduler.DIAS_POR_CODIGO[self.dias]

    def clean(self):
        if self.inicio is not None and self.fin is not None and self.fin <= self.inicio:
            raise ValidationError({"fin": "La hora de fin debe ser posterior a la de inicio."})
