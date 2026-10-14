"""Carga datos de demostración con estilo de universidad mexicana.

Uso:
    python manage.py seed_demo              # carga catálogo (borra el anterior)
    python manage.py seed_demo --generar    # además ejecuta el algoritmo
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from generator import services
from generator.models import Asignacion, Materia, Profesor, ProfesorMateria, Salon

COMPU = "Ingeniería en Computación"
ADMIN = "Administración"
CONTA = "Contaduría"

# (clave, nombre, carrera, semestre, horas/semana, sesiones, tipo de salón, turno)
MATERIAS = [
    ("COM11101", "Cálculo Diferencial", COMPU, 1, 4, 2, "Butaca", "Manana"),
    ("COM11102", "Álgebra Superior", COMPU, 1, 4, 2, "Butaca", "Manana"),
    ("COM11103", "Programación I", COMPU, 1, 5, 2, "Computadora", "Manana"),
    ("COM11104", "Introducción a la Ingeniería", COMPU, 1, 2, 1, "Butaca", "Manana"),
    ("COM11105", "Comunicación Oral y Escrita", COMPU, 1, 3, 1, "Butaca", "Tarde"),
    ("COM13101", "Estructuras de Datos", COMPU, 3, 5, 2, "Computadora", "Manana"),
    ("COM13102", "Ecuaciones Diferenciales", COMPU, 3, 4, 2, "Butaca", "Manana"),
    ("COM13103", "Bases de Datos", COMPU, 3, 4, 2, "Computadora", "Tarde"),
    ("COM13104", "Probabilidad y Estadística", COMPU, 3, 4, 2, "Butaca", "Tarde"),
    ("COM13105", "Arquitectura de Computadoras", COMPU, 3, 3, 1, "Laboratorio", "Tarde"),
    ("COM15101", "Ingeniería de Software", COMPU, 5, 4, 2, "Butaca", "Noche"),
    ("COM15102", "Redes de Computadoras", COMPU, 5, 4, 2, "Computadora", "Noche"),
    ("COM15103", "Sistemas Operativos", COMPU, 5, 4, 2, "Computadora", "Tarde"),
    ("COM15104", "Inteligencia de Negocios", COMPU, 5, 3, 1, "Computadora", "Noche"),
    ("ADM11101", "Fundamentos de Administración", ADMIN, 1, 4, 2, "Butaca", "Manana"),
    ("ADM11102", "Matemáticas Financieras", ADMIN, 1, 4, 2, "Butaca", "Manana"),
    ("ADM11103", "Microeconomía", ADMIN, 1, 4, 2, "Butaca", "Tarde"),
    ("ADM11104", "Informática Administrativa", ADMIN, 1, 2, 1, "Computadora", "Manana"),
    ("ADM13101", "Mercadotecnia", ADMIN, 3, 4, 2, "Butaca", "Tarde"),
    ("ADM13102", "Derecho Mercantil", ADMIN, 3, 3, 1, "Butaca", "Tarde"),
    ("ADM13103", "Estadística para los Negocios", ADMIN, 3, 4, 2, "Computadora", "Tarde"),
    ("CON11101", "Contabilidad Financiera I", CONTA, 1, 5, 2, "Butaca", "Noche"),
    ("CON11102", "Derecho Fiscal", CONTA, 1, 4, 2, "Butaca", "Noche"),
    ("CON11103", "Hoja de Cálculo Aplicada", CONTA, 1, 2, 1, "Computadora", "Noche"),
    ("CON13101", "Costos", CONTA, 3, 4, 2, "Butaca", "Noche"),
    ("CON13102", "Auditoría I", CONTA, 3, 4, 2, "Butaca", "Noche"),
]

# (nombre, correo, dedicación, claves de materias que imparte)
PROFESORES = [
    ("Dra. María Fernanda López Herrera", "mflopez", "Tiempo completo", ["COM11101", "COM13102"]),
    ("Mtro. José Luis Ramírez Ortega", "jlramirez", "Tiempo completo", ["COM11103", "COM13101"]),
    ("Ing. Ana Sofía Castillo Mendoza", "ascastillo", "Asignatura", ["COM13103", "COM15103"]),
    ("Dr. Ricardo Hernández Salinas", "rhernandez", "Tiempo completo", ["COM11102", "COM13104"]),
    (
        "Mtra. Guadalupe Torres Aguilar",
        "gtorres",
        "Asignatura",
        ["COM11104", "COM11105", "ADM13102"],
    ),
    ("Ing. Alejandro Vázquez Rojas", "avazquez", "Asignatura", ["COM13105", "COM15102"]),
    ("Mtro. Carlos Eduardo Navarro Ruiz", "cenavarro", "Asignatura", ["COM15101", "COM15104"]),
    ("Lic. Patricia Morales Domínguez", "pmorales", "Tiempo completo", ["ADM11101", "ADM13101"]),
    ("Act. Jorge Alberto Cruz Medina", "jacruz", "Asignatura", ["ADM11102", "ADM13103"]),
    ("Dra. Laura Elena Sánchez Pineda", "lesanchez", "Medio tiempo", ["ADM11103", "ADM11104"]),
    ("C.P. Roberto Jiménez Flores", "rjimenez", "Asignatura", ["CON11101", "CON13101"]),
    ("Lic. Mónica Gutiérrez Estrada", "mgutierrez", "Asignatura", ["CON11102", "CON11103"]),
    ("C.P. Fernando Reyes Campos", "freyes", "Asignatura", ["CON13102"]),
]

COMPLETO = "0-10,11-20,21-30,"
SIN_NOCHE = "0-10,11-20,x,"
# (clave, tipo, lun, mar, mie, jue, vie)
SALONES = [
    ("A-101", "Butaca", COMPLETO, COMPLETO, COMPLETO, COMPLETO, COMPLETO),
    ("A-102", "Butaca", COMPLETO, COMPLETO, COMPLETO, COMPLETO, COMPLETO),
    ("A-201", "Butaca", SIN_NOCHE, SIN_NOCHE, SIN_NOCHE, SIN_NOCHE, SIN_NOCHE),
    (
        "B-105",
        "Butaca",
        "x,11-20,21-30,",
        "x,11-20,21-30,",
        "x,11-20,21-30,",
        "x,11-20,21-30,",
        COMPLETO,
    ),
    ("LC-1", "Computadora", COMPLETO, COMPLETO, COMPLETO, COMPLETO, COMPLETO),
    ("LC-2", "Computadora", SIN_NOCHE, SIN_NOCHE, SIN_NOCHE, SIN_NOCHE, "0-10,x,x,"),
    (
        "LE-Electrónica",
        "Laboratorio",
        "x,11-20,x,",
        "x,11-20,x,",
        "x,11-20,x,",
        "x,11-20,x,",
        "x,11-20,x,",
    ),
]


class Command(BaseCommand):
    help = "Carga datos de demostración (carreras, semestres, profesores y salones)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--generar", action="store_true", help="Ejecuta el algoritmo tras cargar los datos."
        )
        parser.add_argument(
            "--sin-usuario", action="store_true", help="No crear el usuario demo/demo."
        )

    @transaction.atomic
    def handle(self, *args, **options):
        Asignacion.objects.all().delete()
        ProfesorMateria.objects.all().delete()
        Profesor.objects.all().delete()
        Materia.objects.all().delete()
        Salon.objects.all().delete()

        Materia.objects.bulk_create(
            Materia(
                clave=clave,
                nombre=nombre,
                carrera=carrera,
                semestre=semestre,
                horas=horas,
                dias=sesiones,
                tipo=tipo,
                preferencia=turno,
                periodo="2026-1",
            )
            for clave, nombre, carrera, semestre, horas, sesiones, tipo, turno in MATERIAS
        )
        Salon.objects.bulk_create(
            Salon(clave=c, tipo=t, lun=lu, mar=ma, mier=mi, jue=ju, vie=vi)
            for c, t, lu, ma, mi, ju, vi in SALONES
        )
        for nombre, usuario, dedicacion, claves in PROFESORES:
            profesor = Profesor.objects.create(
                nombre=nombre, correo=f"{usuario}@universidad.edu.mx", horario=dedicacion
            )
            ProfesorMateria.objects.bulk_create(
                ProfesorMateria(profesor=profesor, materia_id=clave) for clave in claves
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Cargados {Profesor.objects.count()} profesores, {Materia.objects.count()} "
                f"materias, {Salon.objects.count()} salones y "
                f"{ProfesorMateria.objects.count()} clases."
            )
        )

        if not options["sin_usuario"]:
            User = get_user_model()
            user, creado = User.objects.get_or_create(
                username="demo", defaults={"first_name": "Usuario", "last_name": "Demo"}
            )
            if creado:
                user.is_staff = True
                user.is_superuser = True
                user.set_password("demo")
                user.save()
                self.stdout.write(
                    self.style.WARNING(
                        "Usuario de demostración: demo / demo (sólo para desarrollo local)."
                    )
                )

        if options["generar"]:
            resultado = services.generar()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Algoritmo: {len(resultado.colocadas)} clases asignadas, "
                    f"{len(resultado.sin_asignar)} sin asignar."
                )
            )
