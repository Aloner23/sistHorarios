import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from generator.models import Asignacion, Materia, Profesor, ProfesorMateria, Salon


@pytest.fixture
def materia(db):
    return Materia.objects.create(
        clave="COM101", nombre="Cálculo", horas=4, semestre=1, carrera="Computación"
    )


@pytest.fixture
def profesor(db):
    return Profesor.objects.create(nombre="Ana Pérez")


def test_profesor_puede_tener_varias_materias(profesor, materia):
    # Con el OneToOneField original esto era imposible.
    otra = Materia.objects.create(
        clave="COM102", nombre="Álgebra", horas=4, semestre=1, carrera="X"
    )
    ProfesorMateria.objects.create(profesor=profesor, materia=materia)
    ProfesorMateria.objects.create(profesor=profesor, materia=otra)
    assert profesor.materias.count() == 2


def test_materia_puede_tener_varios_profesores(profesor, materia):
    otro = Profesor.objects.create(nombre="Luis Gómez")
    ProfesorMateria.objects.create(profesor=profesor, materia=materia)
    ProfesorMateria.objects.create(profesor=otro, materia=materia)
    assert materia.profesores.count() == 2


def test_profesor_materia_es_unica(profesor, materia):
    ProfesorMateria.objects.create(profesor=profesor, materia=materia)
    with pytest.raises(IntegrityError):
        ProfesorMateria.objects.create(profesor=profesor, materia=materia)


def test_salon_valida_formato_de_disponibilidad(db):
    salon = Salon(clave="A-1", lun="0-10,11-20")
    with pytest.raises(ValidationError):
        salon.full_clean()
    Salon(clave="A-2", lun="x,11-20,21-30,").full_clean()


def test_asignacion_horario_legible_y_validacion(profesor, materia):
    clase = ProfesorMateria.objects.create(profesor=profesor, materia=materia)
    salon = Salon.objects.create(clave="A-1")
    a = Asignacion(clase=clase, salon=salon, dias="LM", inicio=0, fin=4)
    a.full_clean()
    a.save()
    assert a.horario == "7:00–9:00"
    assert a.dias_indices == (0, 2)
    assert clase.asignada
    with pytest.raises(ValidationError):
        Asignacion(clase=clase, salon=salon, dias="LM", inicio=4, fin=4).clean()


def test_borrar_profesor_borra_sus_clases(profesor, materia):
    ProfesorMateria.objects.create(profesor=profesor, materia=materia)
    profesor.delete()
    assert not ProfesorMateria.objects.exists()
