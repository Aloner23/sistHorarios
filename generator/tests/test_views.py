import pytest
from django.urls import reverse

from generator.models import Asignacion, Materia, Profesor, ProfesorMateria, Salon

pytestmark = pytest.mark.django_db


def test_login_publico_y_dashboard_protegido(client):
    assert client.get(reverse("login")).status_code == 200
    r = client.get(reverse("dashboard"))
    assert r.status_code == 302 and reverse("login") in r.url


def test_login_con_usuario_demo(client, seed):
    r = client.post(reverse("login"), {"username": "demo", "password": "demo"})
    assert r.status_code == 302 and r.url == reverse("dashboard")


def test_paginas_principales_responden_200(cliente, seed_generado):
    p = Profesor.objects.first()
    pm = ProfesorMateria.objects.first()
    s = Salon.objects.first()
    urls = [
        reverse("dashboard"),
        reverse("profesores"),
        reverse("materias"),
        reverse("salones"),
        reverse("horarioGrupo"),
        reverse("horarioGrupo") + "?carrera=Contaduría&semestre=1",
        reverse("horario", args=[p.pk]),
        reverse("horarioSalon", args=[s.pk]),
        reverse("anadirProfesorMateria", args=[p.pk]),
        reverse("asignaSalon", args=[pm.profesor_id, pm.materia_id]),
        reverse("anadir"),
        reverse("editar", args=[p.pk]),
    ]
    for url in urls:
        assert cliente.get(url).status_code == 200, url


def test_horario_muestra_materias_en_la_grilla(cliente, seed_generado):
    a = Asignacion.objects.select_related("clase").first()
    r = cliente.get(reverse("horario", args=[a.clase.profesor_id]))
    assert a.clase.materia_id in r.content.decode()


def test_404_en_objetos_inexistentes(cliente, db):
    assert cliente.get(reverse("horario", args=[999])).status_code == 404
    assert cliente.get(reverse("horarioSalon", args=["NOEXISTE"])).status_code == 404


def test_acciones_destructivas_requieren_post(cliente, seed):
    p = Profesor.objects.first()
    assert cliente.get(reverse("eliminar", args=[p.pk])).status_code == 405
    assert Profesor.objects.filter(pk=p.pk).exists()


def test_crud_profesor(cliente, db):
    r = cliente.post(reverse("anadir"), {"nombre": "Nuevo Profe", "correo": "", "horario": "x"})
    assert r.status_code == 302
    p = Profesor.objects.get(nombre="Nuevo Profe")
    cliente.post(reverse("editar", args=[p.pk]), {"nombre": "Editado", "correo": "", "horario": ""})
    p.refresh_from_db()
    assert p.nombre == "Editado"
    cliente.post(reverse("eliminar", args=[p.pk]))
    assert not Profesor.objects.filter(pk=p.pk).exists()


def test_agregar_y_quitar_materia_sin_inyeccion_sql(cliente, db):
    p = Profesor.objects.create(nombre="Ana")
    clave = "X'); DROP TABLE materias;--"
    Materia.objects.create(clave=clave, nombre="Rara", horas=2, semestre=1, carrera="C")
    cliente.post(reverse("enterProfesorMateria", args=[p.pk, clave]))
    assert ProfesorMateria.objects.filter(profesor=p, materia_id=clave).exists()
    cliente.post(reverse("eliminarProfesorMateria", args=[clave, p.pk]))
    assert not ProfesorMateria.objects.exists()
    assert Materia.objects.filter(pk=clave).exists()


def test_generar_desde_dashboard(cliente, seed):
    r = cliente.post(reverse("generar"), {"carrera": "", "semestre": ""})
    assert r.status_code == 302
    assert Asignacion.objects.count() == ProfesorMateria.objects.count()
    cliente.post(reverse("reiniciar"))
    assert not Asignacion.objects.exists()


def test_asignacion_manual_valida_choques(cliente, seed_generado):
    a = Asignacion.objects.select_related("salon", "clase__materia").first()
    otra = (
        ProfesorMateria.objects.exclude(pk=a.clase_id)
        .filter(materia__tipo=a.salon.tipo, materia__dias=len(a.dias_indices))
        .first()
    )
    Asignacion.objects.filter(clase=otra).delete()
    url = reverse("asignaSalon", args=[otra.profesor_id, otra.materia_id])
    datos = {"salon": a.salon_id, "dias": a.dias, "inicio": a.inicio, "fin": a.fin}
    r = cliente.post(url, datos)
    assert r.status_code == 200 and "ocupado" in r.content.decode()
    assert not Asignacion.objects.filter(clase=otra).exists()
