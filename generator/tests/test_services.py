import itertools

import pytest

from generator import scheduler, services
from generator.models import Asignacion, ProfesorMateria, Salon


def _traslapes(asignaciones):
    for a, b in itertools.combinations(asignaciones, 2):
        mismo_dia = set(a.dias_indices) & set(b.dias_indices)
        if mismo_dia and scheduler.se_traslapan((a.inicio, a.fin), (b.inicio, b.fin)):
            yield a, b


def test_seed_demo_genera_horario_completo_sin_choques(seed_generado):
    asignaciones = list(Asignacion.objects.select_related("clase__materia", "salon"))
    assert len(asignaciones) == ProfesorMateria.objects.count() > 0
    for a, b in _traslapes(asignaciones):
        assert a.salon_id != b.salon_id
        assert a.clase.profesor_id != b.clase.profesor_id
        assert services.grupo_de(a.clase.materia) != services.grupo_de(b.clase.materia)
    for a in asignaciones:
        m = a.clase.materia
        assert a.salon.tipo == m.tipo
        assert (a.fin - a.inicio) * len(a.dias_indices) == m.horas * 2
        # Cabe dentro de algún bloque disponible del salón cada día.
        for d in a.dias_indices:
            bloques = scheduler.parse_disponibilidad(a.salon.disponibilidad[d])
            assert any(b and b[0] <= a.inicio and a.fin <= b[1] for b in bloques)


def test_generar_es_idempotente(seed_generado):
    total = Asignacion.objects.count()
    resultado = services.generar()
    assert not resultado.colocadas
    assert Asignacion.objects.count() == total


def test_generar_filtrado_por_grupo(seed):
    services.generar(carrera="Contaduría", semestre=1)
    carreras = set(Asignacion.objects.values_list("clase__materia__carrera", flat=True))
    assert carreras == {"Contaduría"}


def test_conflictos_detecta_salon_profesor_y_tipo(seed_generado):
    a = Asignacion.objects.select_related("clase__materia", "salon").first()
    otra = ProfesorMateria.objects.exclude(pk=a.clase_id).filter(materia__tipo=a.salon.tipo).first()
    errores = services.conflictos(otra, a.salon, a.dias, a.inicio, a.fin)
    assert any("ocupado" in e for e in errores)

    distinto = Salon.objects.exclude(tipo=a.clase.materia.tipo).first()
    errores = services.conflictos(a.clase, distinto, a.dias, a.inicio, a.fin)
    assert any("tipo" in e for e in errores)


@pytest.mark.parametrize(("inicio", "fin"), [(4, 4), (6, 2)])
def test_conflictos_rechaza_rango_invalido(seed, inicio, fin):
    clase = ProfesorMateria.objects.first()
    assert services.conflictos(clase, Salon.objects.first(), "LM", inicio, fin)
