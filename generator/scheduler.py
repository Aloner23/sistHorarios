"""Algoritmo de asignación de horarios (sin dependencias de Django).

Este módulo es la versión refactorizada y testeable de ``generator/pr.py``
(el script original con consultas ``pymysql``). La idea del algoritmo se
conserva:

* El día se divide en **medias horas** a partir de las 7:00: el índice ``0``
  es 7:00 y el ``30`` es 22:00.
* Cada salón publica, por día, una cadena de disponibilidad con tres bloques
  (mañana, tarde y noche), p. ej. ``"0-10,11-20,21-30,"``; ``x`` marca un
  bloque cerrado. Es el mismo formato que usaba la tabla ``salones``.
* Cada materia tiene un turno preferido (``Manana``, ``Tarde``, ``Noche``),
  un tipo de salón (``Butaca``, ``Computadora``…), horas por semana y número
  de sesiones por semana.
* Para cada clase (profesor + materia) se busca, salón por salón, el primer
  hueco libre dentro del bloque del turno preferido, en pares de días
  Lun/Mié o Mar/Jue (equivalente a ``depurador_hora_salon`` +
  ``asignacionHorario`` + ``modificadorSalon`` del original).

Correcciones respecto a ``pr.py`` (documentadas también en el README):

1. ``asignacionHorario`` no reiniciaba el contador de día entre salones ni
   salía del ciclo externo: terminaba usando el *último* salón disponible y
   podía indexar fuera de la tupla. Ahora se toma el primer salón válido.
2. ``modificadorSalon`` asignaba la clase aunque no cupiera en el bloque y,
   al "cerrar" un bloque, reconstruía mal la cadena (p. ej. con preferencia
   ``Manana`` sobrescribía el inicio del bloque de la tarde). Ahora una clase
   sólo se coloca si cabe completa y nunca invade otro bloque.
3. Las horas por sesión se calculaban como ``int(horas / dias)``, perdiendo
   media sesión con horas impares (5 h en 2 sesiones → 2 h). Ahora se usan
   medias horas: 5 h en 2 sesiones → 2.5 h por sesión.
4. Materias de una sola sesión semanal se asignaban igualmente a dos días.
5. No se verificaba que un profesor (ni un grupo carrera/semestre) tuviera dos
   clases a la misma hora en salones distintos. Ahora se respeta.
6. Si no había salón disponible el original fallaba con ``UnboundLocalError``;
   ahora la clase se reporta como "sin asignar".
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

# --- Constantes de la rejilla ------------------------------------------------

HORA_INICIO_MINUTOS = 7 * 60
TOTAL_MEDIAS_HORAS = 30  # 7:00 → 22:00
DIAS_SEMANA = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
JORNADA_COMPLETA = "0-10,11-20,21-30,"

TURNOS = ("Manana", "Tarde", "Noche")
# Punto de referencia de cada turno (``preferenciaPuntos`` en pr.py).
PUNTOS_TURNO = {"Manana": 0, "Tarde": 11, "Noche": 21}
INDICE_BLOQUE = {"Manana": 0, "Tarde": 1, "Noche": 2}

# Combinaciones de días permitidas por número de sesiones semanales.
DIAS_POR_CODIGO: dict[str, tuple[int, ...]] = {
    "LM": (0, 2),
    "MJ": (1, 3),
    "L": (0,),
    "M": (1,),
    "X": (2,),
    "J": (3,),
    "V": (4,),
}
OPCIONES_POR_SESIONES = {2: ("LM", "MJ"), 1: ("L", "M", "X", "J", "V")}

Bloque = tuple[int, int] | None
Intervalo = tuple[int, int]


# --- Utilidades --------------------------------------------------------------


def etiqueta_hora(indice: int) -> str:
    """Convierte un índice de media hora en texto ``H:MM`` (0 → ``7:00``)."""
    minutos = HORA_INICIO_MINUTOS + indice * 30
    return f"{minutos // 60}:{minutos % 60:02d}"


def medias_horas_por_sesion(horas_semana: int, sesiones: int) -> int:
    """Duración de cada sesión en medias horas."""
    if sesiones < 1 or horas_semana < 1:
        raise ValueError("horas y sesiones deben ser positivas")
    total = horas_semana * 2
    if total % sesiones:
        raise ValueError(f"{horas_semana} h no se reparten en {sesiones} sesiones de media hora")
    return total // sesiones


def parse_disponibilidad(cadena: str) -> list[Bloque]:
    """``"0-10,x,21-30,"`` → ``[(0, 10), None, (21, 30)]``."""
    bloques: list[Bloque] = []
    for parte in cadena.split(","):
        parte = parte.strip()
        if not parte:
            continue
        if parte == "x":
            bloques.append(None)
            continue
        inicio, fin = (int(n) for n in parte.split("-"))
        bloques.append((inicio, fin) if fin > inicio else None)
    if len(bloques) != len(TURNOS):
        raise ValueError(f"Se esperaban 3 bloques en {cadena!r}")
    return bloques


def format_disponibilidad(bloques: Sequence[Bloque]) -> str:
    return "".join("x," if b is None else f"{b[0]}-{b[1]}," for b in bloques)


def bloque_en_turno(inicio: int, fin: int, turno: str) -> bool:
    """Regla original de ``depurador_hora_salon`` para decidir si un bloque
    pertenece al turno: contiene el punto del turno, o empieza dentro de los
    10 medios horarios siguientes (bloque parcialmente consumido)."""
    punto = PUNTOS_TURNO[turno]
    return (punto >= inicio and fin > punto) or (punto < inicio < punto + 10)


def se_traslapan(a: Intervalo, b: Intervalo) -> bool:
    return a[0] < b[1] and b[0] < a[1]


# --- Modelo de datos del algoritmo ------------------------------------------


@dataclass(frozen=True)
class SalonDisp:
    clave: str
    tipo: str
    disponibilidad: Sequence[str]  # cinco cadenas, lunes a viernes

    def bloque(self, dia: int, turno: str) -> Bloque:
        bloque = parse_disponibilidad(self.disponibilidad[dia])[INDICE_BLOQUE[turno]]
        if bloque is None or not bloque_en_turno(*bloque, turno):
            return None
        return bloque


@dataclass(frozen=True)
class Clase:
    id: int
    profesor_id: int
    materia: str
    tipo: str
    turno: str
    horas: int
    sesiones: int = 2
    grupo: str = ""

    @property
    def duracion(self) -> int:
        return medias_horas_por_sesion(self.horas, self.sesiones)


@dataclass(frozen=True)
class Colocacion:
    clase_id: int
    salon: str
    dias: str  # código de DIAS_POR_CODIGO
    inicio: int
    fin: int

    @property
    def dias_indices(self) -> tuple[int, ...]:
        return DIAS_POR_CODIGO[self.dias]


@dataclass(frozen=True)
class Ocupacion:
    """Asignación ya existente que el algoritmo debe respetar."""

    salon: str
    profesor_id: int
    dias: str
    inicio: int
    fin: int
    grupo: str = ""


@dataclass
class Resultado:
    colocadas: list[Colocacion] = field(default_factory=list)
    sin_asignar: list[Clase] = field(default_factory=list)


# --- Algoritmo ---------------------------------------------------------------


class _Agenda:
    """Intervalos ocupados por (recurso, día)."""

    def __init__(self) -> None:
        self._ocupado: dict[tuple[object, int], list[Intervalo]] = defaultdict(list)

    def libre(self, recurso: object, dia: int, intervalo: Intervalo) -> bool:
        return not any(se_traslapan(intervalo, o) for o in self._ocupado[(recurso, dia)])

    def ocupar(self, recurso: object, dia: int, intervalo: Intervalo) -> None:
        self._ocupado[(recurso, dia)].append(intervalo)


def _primer_hueco(
    agenda: _Agenda,
    recursos: Sequence[object],
    dias: Sequence[int],
    bloques: Sequence[tuple[int, int]],
    duracion: int,
) -> int | None:
    """Primer inicio ``s`` tal que ``[s, s+duracion)`` cabe en el bloque de
    cada día y está libre para todos los recursos (salón, profesor, grupo)."""
    desde = max(b[0] for b in bloques)
    hasta = min(b[1] for b in bloques)
    for inicio in range(desde, hasta - duracion + 1):
        intervalo = (inicio, inicio + duracion)
        if all(agenda.libre(r, d, intervalo) for r in recursos for d in dias):
            return inicio
    return None


def generar_horario(
    clases: Iterable[Clase],
    salones: Sequence[SalonDisp],
    ocupadas: Iterable[Ocupacion] = (),
    evitar_choques_de_grupo: bool = True,
) -> Resultado:
    """Asigna salón, días y hora a cada clase con una estrategia *greedy*.

    Las clases se procesan en el orden recibido; para cada una se recorren
    los salones del tipo requerido (en orden) y las combinaciones de días
    permitidas, y se toma el primer hueco que cabe en el bloque del turno
    preferido sin chocar con el salón, el profesor ni el grupo.
    """
    agenda = _Agenda()
    for o in ocupadas:
        for dia in DIAS_POR_CODIGO[o.dias]:
            agenda.ocupar(("salon", o.salon), dia, (o.inicio, o.fin))
            agenda.ocupar(("prof", o.profesor_id), dia, (o.inicio, o.fin))
            if evitar_choques_de_grupo and o.grupo:
                agenda.ocupar(("grupo", o.grupo), dia, (o.inicio, o.fin))

    resultado = Resultado()
    for clase in clases:
        colocacion = _colocar(clase, salones, agenda, evitar_choques_de_grupo)
        if colocacion is None:
            resultado.sin_asignar.append(clase)
        else:
            resultado.colocadas.append(colocacion)
    return resultado


def _colocar(
    clase: Clase, salones: Sequence[SalonDisp], agenda: _Agenda, evitar_grupo: bool
) -> Colocacion | None:
    duracion = clase.duracion
    opciones = OPCIONES_POR_SESIONES.get(clase.sesiones)
    if opciones is None:
        return None
    for salon in salones:
        if salon.tipo != clase.tipo:
            continue
        for codigo in opciones:
            dias = DIAS_POR_CODIGO[codigo]
            bloques = [salon.bloque(d, clase.turno) for d in dias]
            if any(b is None for b in bloques):
                continue
            recursos: list[object] = [("salon", salon.clave), ("prof", clase.profesor_id)]
            if evitar_grupo and clase.grupo:
                recursos.append(("grupo", clase.grupo))
            inicio = _primer_hueco(agenda, recursos, dias, bloques, duracion)  # type: ignore[arg-type]
            if inicio is None:
                continue
            intervalo = (inicio, inicio + duracion)
            for d in dias:
                for r in recursos:
                    agenda.ocupar(r, d, intervalo)
            return Colocacion(clase.id, salon.clave, codigo, *intervalo)
    return None


def construir_grilla(
    entradas: Iterable[tuple[Sequence[int], int, int, str]],
) -> list[dict]:
    """Rejilla de 30 filas (medias horas) × 5 días para mostrar un horario.

    ``entradas`` son tuplas ``(dias, inicio, fin, texto)``; ``fin`` es
    exclusivo (la vista original lo trataba como inclusivo y pintaba una
    media hora de más).
    """
    filas = [
        {"hora": etiqueta_hora(i), "celdas": [""] * len(DIAS_SEMANA)}
        for i in range(TOTAL_MEDIAS_HORAS)
    ]
    for dias, inicio, fin, texto in entradas:
        for i in range(max(inicio, 0), min(fin, TOTAL_MEDIAS_HORAS)):
            for d in dias:
                celda = filas[i]["celdas"][d]
                filas[i]["celdas"][d] = f"{celda} / {texto}" if celda else texto
    return filas
