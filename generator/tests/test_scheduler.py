"""Pruebas del algoritmo puro (sin base de datos)."""

import itertools

import pytest

from generator import scheduler as s
from generator.scheduler import Clase, Ocupacion, SalonDisp

COMPLETO = [s.JORNADA_COMPLETA] * 5


def salon(clave="A-1", tipo="Butaca", disp=None):
    return SalonDisp(clave, tipo, disp or COMPLETO)


def clase(i, prof=1, turno="Manana", horas=4, sesiones=2, tipo="Butaca", grupo=""):
    return Clase(i, prof, f"M{i}", tipo, turno, horas, sesiones, grupo)


def ocupaciones_por_dia(colocadas, clases):
    por_id = {c.id: c for c in clases}
    for col in colocadas:
        for d in col.dias_indices:
            yield col, por_id[col.clase_id], d


def assert_sin_traslapes(resultado, clases):
    items = list(ocupaciones_por_dia(resultado.colocadas, clases))
    for (c1, k1, d1), (c2, k2, d2) in itertools.combinations(items, 2):
        if d1 != d2 or not s.se_traslapan((c1.inicio, c1.fin), (c2.inicio, c2.fin)):
            continue
        assert c1.salon != c2.salon, f"salón {c1.salon} duplicado: {k1} / {k2}"
        assert k1.profesor_id != k2.profesor_id, f"profesor duplicado: {k1} / {k2}"
        if k1.grupo:
            assert k1.grupo != k2.grupo, f"grupo duplicado: {k1} / {k2}"


# --- utilidades --------------------------------------------------------------


@pytest.mark.parametrize(
    ("indice", "texto"), [(0, "7:00"), (1, "7:30"), (10, "12:00"), (30, "22:00")]
)
def test_etiqueta_hora(indice, texto):
    assert s.etiqueta_hora(indice) == texto


def test_parse_y_format_disponibilidad_ida_y_vuelta():
    cadena = "0-10,x,21-30,"
    bloques = s.parse_disponibilidad(cadena)
    assert bloques == [(0, 10), None, (21, 30)]
    assert s.format_disponibilidad(bloques) == cadena


def test_parse_disponibilidad_rechaza_formato_invalido():
    with pytest.raises(ValueError):
        s.parse_disponibilidad("0-10,11-20,")


def test_medias_horas_por_sesion_no_pierde_media_hora():
    # pr.py usaba int(5 / 2) = 2 horas; ahora son 2.5 h = 5 medias horas.
    assert s.medias_horas_por_sesion(5, 2) == 5
    assert s.medias_horas_por_sesion(4, 2) == 4
    assert s.medias_horas_por_sesion(3, 1) == 6


@pytest.mark.parametrize(
    ("bloque", "turno", "esperado"),
    [
        ((0, 10), "Manana", True),
        ((4, 10), "Manana", True),  # bloque ya consumido parcialmente
        ((11, 20), "Manana", False),
        ((11, 20), "Tarde", True),
        ((21, 30), "Noche", True),
        ((0, 10), "Noche", False),
    ],
)
def test_bloque_en_turno(bloque, turno, esperado):
    assert s.bloque_en_turno(*bloque, turno) is esperado


# --- algoritmo ---------------------------------------------------------------


def test_asigna_en_bloque_del_turno_preferido():
    clases = [
        clase(1, turno="Manana"),
        clase(2, prof=2, turno="Tarde"),
        clase(3, prof=3, turno="Noche"),
    ]
    r = s.generar_horario(clases, [salon()])
    assert not r.sin_asignar
    rangos = {"Manana": (0, 10), "Tarde": (11, 20), "Noche": (21, 30)}
    for col in r.colocadas:
        turno = clases[col.clase_id - 1].turno
        a, b = rangos[turno]
        assert a <= col.inicio and col.fin <= b


def test_horas_semanales_se_respetan():
    clases = [clase(1, horas=4), clase(2, prof=2, horas=5), clase(3, prof=3, horas=3, sesiones=1)]
    r = s.generar_horario(clases, [salon(), salon("A-2")])
    assert not r.sin_asignar
    for col in r.colocadas:
        k = clases[col.clase_id - 1]
        medias_semana = (col.fin - col.inicio) * len(col.dias_indices)
        assert medias_semana == k.horas * 2
        assert len(col.dias_indices) == k.sesiones


def test_no_traslapa_salon_ni_profesor():
    # El mismo profesor con tres materias de mañana y un solo salón.
    clases = [clase(i, prof=1) for i in range(1, 4)]
    r = s.generar_horario(clases, [salon()])
    assert len(r.colocadas) == 3
    assert_sin_traslapes(r, clases)


def test_profesor_no_se_duplica_en_salones_distintos():
    # Bug del original: sólo revisaba el salón. Dos salones libres a la misma
    # hora no deben usarse para el mismo profesor simultáneamente.
    clases = [clase(1, prof=7), clase(2, prof=7)]
    r = s.generar_horario(clases, [salon("A-1"), salon("A-2")])
    assert len(r.colocadas) == 2
    assert_sin_traslapes(r, clases)


def test_grupo_no_tiene_dos_clases_a_la_vez():
    clases = [clase(1, prof=1, grupo="Compu|1"), clase(2, prof=2, grupo="Compu|1")]
    r = s.generar_horario(clases, [salon("A-1"), salon("A-2")])
    assert_sin_traslapes(r, clases)


def test_respeta_tipo_de_salon():
    clases = [clase(1, tipo="Computadora")]
    r = s.generar_horario(clases, [salon("A-1", "Butaca"), salon("LC-1", "Computadora")])
    assert r.colocadas[0].salon == "LC-1"


def test_reporta_sin_asignar_cuando_no_cabe():
    # pr.py fallaba con UnboundLocalError; ahora se reporta.
    clases = [clase(1, tipo="Laboratorio")]
    r = s.generar_horario(clases, [salon()])
    assert r.sin_asignar == clases and not r.colocadas


def test_no_asigna_si_la_clase_no_cabe_en_el_bloque():
    # 6 h en 1 sesión = 12 medias horas > bloque de 10; pr.py la asignaba igual.
    r = s.generar_horario([clase(1, horas=6, sesiones=1)], [salon()])
    assert r.sin_asignar


def test_bloque_cerrado_no_se_usa():
    disp = ["x,11-20,21-30,"] * 5
    r = s.generar_horario([clase(1, turno="Manana")], [salon(disp=disp)])
    assert r.sin_asignar


def test_llena_un_bloque_y_luego_usa_otro_par_de_dias():
    # Bloque matutino de 10 medias horas, clases de 4 medias horas: caben 2
    # por par de días (LM y MJ) => 4 clases en total, la quinta no cabe.
    clases = [clase(i, prof=i) for i in range(1, 6)]
    r = s.generar_horario(clases, [salon()])
    assert len(r.colocadas) == 4
    assert {c.dias for c in r.colocadas} == {"LM", "MJ"}
    assert len(r.sin_asignar) == 1
    assert_sin_traslapes(r, clases)


def test_respeta_ocupaciones_existentes():
    previa = Ocupacion(salon="A-1", profesor_id=99, dias="LM", inicio=0, fin=10)
    r = s.generar_horario([clase(1)], [salon()], ocupadas=[previa])
    col = r.colocadas[0]
    assert col.dias == "MJ"


def test_clase_de_una_sesion_usa_un_solo_dia():
    r = s.generar_horario([clase(1, horas=2, sesiones=1)], [salon()])
    assert len(r.colocadas[0].dias_indices) == 1


def test_construir_grilla_fin_exclusivo():
    grilla = s.construir_grilla([((0, 2), 0, 4, "MAT")])
    assert len(grilla) == s.TOTAL_MEDIAS_HORAS
    assert [f["celdas"][0] for f in grilla[:5]] == ["MAT"] * 4 + [""]
    assert grilla[0]["celdas"][2] == "MAT" and grilla[0]["celdas"][1] == ""


@pytest.mark.parametrize(
    "recurso",
    [{"prof": 7}, {"grupo": "Compu|1"}],
    ids=["profesor", "grupo"],
)
def test_choque_en_salones_distintos_obliga_a_otra_hora(recurso):
    # A-1 sólo tiene hueco para una clase (L/M de 0 a 4, M/J cerrado), así que la
    # segunda clase debe ir a A-2. Si el algoritmo ignorara al profesor o al grupo,
    # la pondría también de 0 a 4 y habría un choque simultáneo en dos salones.
    estrecho = ["0-4,11-20,21-30,", "x,11-20,21-30,"] * 2 + ["x,11-20,21-30,"]
    salones = [salon("A-1", disp=estrecho), salon("A-2")]
    prof = recurso.get("prof")
    clases = [
        clase(1, prof=prof or 1, grupo=recurso.get("grupo", "")),
        clase(2, prof=prof or 2, grupo=recurso.get("grupo", "")),
    ]
    r = s.generar_horario(clases, salones)
    assert len(r.colocadas) == 2
    assert {c.salon for c in r.colocadas} == {"A-1", "A-2"}
    assert_sin_traslapes(r, clases)


def test_sin_evitar_choques_de_grupo_se_permite_simultaneidad():
    estrecho = ["0-4,11-20,21-30,", "x,11-20,21-30,"] * 2 + ["x,11-20,21-30,"]
    salones = [salon("A-1", disp=estrecho), salon("A-2")]
    clases = [clase(1, prof=1, grupo="G"), clase(2, prof=2, grupo="G")]
    r = s.generar_horario(clases, salones, evitar_choques_de_grupo=False)
    assert [(c.dias, c.inicio) for c in r.colocadas] == [("LM", 0), ("LM", 0)]
