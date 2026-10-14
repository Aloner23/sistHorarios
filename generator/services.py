"""Puente entre los modelos de Django y el algoritmo de ``scheduler``."""

from __future__ import annotations

from django.db import transaction
from django.db.models import Case, IntegerField, QuerySet, Value, When

from . import scheduler
from .models import Asignacion, ProfesorMateria, Salon


def grupo_de(materia) -> str:
    return f"{materia.carrera}|{materia.semestre}"


def _salones_disp(salones: QuerySet[Salon]) -> list[scheduler.SalonDisp]:
    return [scheduler.SalonDisp(s.clave, s.tipo, s.disponibilidad) for s in salones]


def _ocupaciones(asignaciones) -> list[scheduler.Ocupacion]:
    return [
        scheduler.Ocupacion(
            salon=a.salon_id,
            profesor_id=a.clase.profesor_id,
            dias=a.dias,
            inicio=a.inicio,
            fin=a.fin,
            grupo=grupo_de(a.clase.materia),
        )
        for a in asignaciones
    ]


def clases_pendientes(carrera: str | None = None, semestre: int | None = None):
    """Clases sin asignación, en el orden que usaba ``algoritmo()`` de pr.py:
    primero turno matutino, luego vespertino y nocturno."""
    qs = ProfesorMateria.objects.filter(asignacion__isnull=True).select_related(
        "materia", "profesor"
    )
    if carrera:
        qs = qs.filter(materia__carrera=carrera)
    if semestre:
        qs = qs.filter(materia__semestre=semestre)
    orden_turno = Case(
        *[When(materia__preferencia=t, then=Value(i)) for i, t in enumerate(scheduler.TURNOS)],
        default=Value(len(scheduler.TURNOS)),
        output_field=IntegerField(),
    )
    return qs.order_by(orden_turno, "materia__semestre", "materia__clave", "profesor__nombre")


@transaction.atomic
def generar(carrera: str | None = None, semestre: int | None = None) -> scheduler.Resultado:
    """Ejecuta el algoritmo sobre las clases pendientes y guarda el resultado."""
    pendientes = list(clases_pendientes(carrera, semestre))
    clases = [
        scheduler.Clase(
            id=pm.pk,
            profesor_id=pm.profesor_id,
            materia=pm.materia_id,
            tipo=pm.materia.tipo,
            turno=pm.materia.preferencia,
            horas=pm.materia.horas,
            sesiones=pm.materia.dias,
            grupo=grupo_de(pm.materia),
        )
        for pm in pendientes
    ]
    existentes = Asignacion.objects.select_related("clase__materia")
    resultado = scheduler.generar_horario(
        clases, _salones_disp(Salon.objects.all()), _ocupaciones(existentes)
    )
    Asignacion.objects.bulk_create(
        Asignacion(clase_id=c.clase_id, salon_id=c.salon, dias=c.dias, inicio=c.inicio, fin=c.fin)
        for c in resultado.colocadas
    )
    return resultado


def conflictos(clase: ProfesorMateria, salon: Salon, dias: str, inicio: int, fin: int) -> list[str]:
    """Valida una asignación manual. Devuelve una lista de mensajes de error."""
    errores: list[str] = []
    if fin <= inicio:
        return ["La hora de fin debe ser posterior a la de inicio."]
    if salon.tipo != clase.materia.tipo:
        errores.append(
            f"El salón {salon} es de tipo {salon.get_tipo_display()} y la materia requiere "
            f"{clase.materia.get_tipo_display()}."
        )
    dias_idx = scheduler.DIAS_POR_CODIGO[dias]
    intervalo = (inicio, fin)
    for d in dias_idx:
        bloques = scheduler.parse_disponibilidad(salon.disponibilidad[d])
        if not any(b and b[0] <= inicio and fin <= b[1] for b in bloques):
            errores.append(
                f"El salón {salon} no está disponible el {scheduler.DIAS_SEMANA[d]} en ese horario."
            )
    otras = (
        Asignacion.objects.exclude(clase=clase)
        .select_related("clase__profesor", "clase__materia")
        .filter(inicio__lt=fin, fin__gt=inicio)
    )
    grupo = grupo_de(clase.materia)
    for a in otras:
        if not set(a.dias_indices) & set(dias_idx) or not scheduler.se_traslapan(
            intervalo, (a.inicio, a.fin)
        ):
            continue
        if a.salon_id == salon.pk:
            errores.append(f"El salón {salon} ya está ocupado por {a.clase}.")
        if a.clase.profesor_id == clase.profesor_id:
            errores.append(f"{clase.profesor} ya imparte {a.clase.materia.clave} a esa hora.")
        elif grupo_de(a.clase.materia) == grupo:
            errores.append(
                f"El grupo {clase.materia.carrera} {clase.materia.semestre}° ya tiene "
                f"{a.clase.materia.clave} a esa hora."
            )
    return errores


def grilla_de(asignaciones, etiqueta) -> list[dict]:
    return scheduler.construir_grilla(
        (a.dias_indices, a.inicio, a.fin, etiqueta(a)) for a in asignaciones
    )
