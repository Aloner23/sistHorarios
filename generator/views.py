from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from . import services
from .forms import AsignacionForm, GenerarForm, ProfesorForm
from .models import Asignacion, Materia, Profesor, ProfesorMateria, Salon


def _carreras_y_semestres():
    carreras = Materia.objects.order_by("carrera").values_list("carrera", flat=True).distinct()
    semestres = Materia.objects.order_by("semestre").values_list("semestre", flat=True).distinct()
    return list(carreras), list(semestres)


@login_required
def dashboard(request):
    carreras, semestres = _carreras_y_semestres()
    total_clases = ProfesorMateria.objects.count()
    asignadas = Asignacion.objects.count()
    context = {
        "stats": {
            "profesores": Profesor.objects.count(),
            "materias": Materia.objects.count(),
            "salones": Salon.objects.count(),
            "clases": total_clases,
            "asignadas": asignadas,
            "pendientes": total_clases - asignadas,
            "avance": round(100 * asignadas / total_clases) if total_clases else 0,
        },
        "form": GenerarForm(carreras=carreras, semestres=semestres),
        "pendientes": services.clases_pendientes()[:10],
        "grupos": Materia.objects.values("carrera", "semestre")
        .annotate(n=Count("clases"), asignadas=Count("clases__asignacion"))
        .order_by("carrera", "semestre"),
    }
    return render(request, "html/dashboard.html", context)


@login_required
@require_POST
def generar(request):
    carreras, semestres = _carreras_y_semestres()
    form = GenerarForm(request.POST, carreras=carreras, semestres=semestres)
    if not form.is_valid():
        messages.error(request, "Filtro no válido.")
        return redirect("dashboard")
    resultado = services.generar(form.cleaned_data["carrera"], form.cleaned_data["semestre"])
    if resultado.colocadas:
        messages.success(request, f"Se asignaron {len(resultado.colocadas)} clases.")
    if resultado.sin_asignar:
        messages.warning(
            request,
            f"{len(resultado.sin_asignar)} clases no cupieron en ningún salón de su turno: "
            + ", ".join(c.materia for c in resultado.sin_asignar[:8]),
        )
    if not resultado.colocadas and not resultado.sin_asignar:
        messages.info(request, "No hay clases pendientes con ese filtro.")
    return redirect("dashboard")


@login_required
@require_POST
def reiniciar(request):
    borradas, _ = Asignacion.objects.all().delete()
    messages.info(request, f"Se eliminaron {borradas} asignaciones.")
    return redirect("dashboard")


# --- Profesores --------------------------------------------------------------


@login_required
def profesores(request):
    profes = Profesor.objects.annotate(
        n_materias=Count("clases", distinct=True),
        n_asignadas=Count("clases__asignacion", distinct=True),
    )
    return render(request, "html/profesores.html", {"profes": profes})


@login_required
def anadirProfesor(request):
    form = ProfesorForm(request.POST or None)
    if form.is_valid():
        profesor = form.save()
        messages.success(request, f"Profesor {profesor} agregado.")
        return redirect("profesores")
    return render(request, "html/form.html", {"form": form, "titulo": "Añadir profesor"})


@login_required
def editarProfesor(request, idprof):
    profesor = get_object_or_404(Profesor, pk=idprof)
    form = ProfesorForm(request.POST or None, instance=profesor)
    if form.is_valid():
        form.save()
        messages.success(request, "Cambios guardados.")
        return redirect("profesores")
    return render(request, "html/form.html", {"form": form, "titulo": f"Editar a {profesor}"})


@login_required
@require_POST
def eliminarProfesor(request, idprof):
    profesor = get_object_or_404(Profesor, pk=idprof)
    profesor.delete()
    messages.info(request, f"Profesor {profesor} eliminado.")
    return redirect("profesores")


@login_required
def horario(request, idprof):
    profesor = get_object_or_404(Profesor, pk=idprof)
    clases = profesor.clases.select_related("materia", "asignacion__salon")
    asignaciones = [c.asignacion for c in clases if c.asignada]
    grilla = services.grilla_de(asignaciones, lambda a: f"{a.clase.materia_id} ({a.salon_id})")
    context = {"profesor": profesor, "clases": clases, "grilla": grilla}
    return render(request, "html/horario.html", context)


@login_required
def anadirProfesorMateria(request, idprof):
    profesor = get_object_or_404(Profesor, pk=idprof)
    materias = Materia.objects.exclude(clases__profesor=profesor)
    context = {"profesor": profesor, "materias": materias}
    return render(request, "html/asignaMateria.html", context)


@login_required
@require_POST
def enterProfesorMateria(request, idprof, materias_clave):
    profesor = get_object_or_404(Profesor, pk=idprof)
    materia = get_object_or_404(Materia, pk=materias_clave)
    _, creada = ProfesorMateria.objects.get_or_create(profesor=profesor, materia=materia)
    if creada:
        messages.success(request, f"{materia.clave} agregada a {profesor}.")
    return redirect("horario", idprof=profesor.pk)


@login_required
@require_POST
def eliminarProfesorMateria(request, materias_clave, idprof):
    clase = get_object_or_404(ProfesorMateria, profesor_id=idprof, materia_id=materias_clave)
    clase.delete()
    messages.info(request, f"{materias_clave} eliminada.")
    return redirect("horario", idprof=idprof)


@login_required
def asignaSalon(request, idprof, materias_clave):
    clase = get_object_or_404(
        ProfesorMateria.objects.select_related("profesor", "materia"),
        profesor_id=idprof,
        materia_id=materias_clave,
    )
    instancia = getattr(clase, "asignacion", None)
    form = AsignacionForm(request.POST or None, instance=instancia, clase=clase)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, f"{clase.materia.clave} asignada.")
        return redirect("horario", idprof=idprof)
    salones = Salon.objects.filter(tipo=clase.materia.tipo)
    context = {"form": form, "clase": clase, "salones": salones}
    return render(request, "html/asignaSalon.html", context)


@login_required
@require_POST
def desasignar(request, idprof, materias_clave):
    Asignacion.objects.filter(clase__profesor_id=idprof, clase__materia_id=materias_clave).delete()
    messages.info(request, f"Se liberó el salón de {materias_clave}.")
    return redirect("horario", idprof=idprof)


# --- Catálogos ---------------------------------------------------------------


@login_required
def materias(request):
    materias = Materia.objects.annotate(
        n_profesores=Count("clases", distinct=True),
        n_asignadas=Count("clases__asignacion", distinct=True),
    )
    return render(request, "html/materias.html", {"materias": materias})


@login_required
def salones(request):
    salones = Salon.objects.annotate(n_clases=Count("asignaciones"))
    return render(request, "html/salones.html", {"salones": salones})


@login_required
def horarioSalon(request, clave):
    salon = get_object_or_404(Salon, pk=clave)
    asignaciones = salon.asignaciones.select_related("clase__materia", "clase__profesor")
    grilla = services.grilla_de(
        asignaciones, lambda a: f"{a.clase.materia_id} · {a.clase.profesor.nombre.split()[0]}"
    )
    context = {"salon": salon, "asignaciones": asignaciones, "grilla": grilla}
    return render(request, "html/horario_salon.html", context)


@login_required
def horarioGrupo(request):
    carreras, semestres = _carreras_y_semestres()
    carrera = request.GET.get("carrera") or (carreras[0] if carreras else "")
    try:
        semestre = int(request.GET.get("semestre") or (semestres[0] if semestres else 1))
    except ValueError:
        semestre = 1
    asignaciones = Asignacion.objects.filter(
        Q(clase__materia__carrera=carrera) & Q(clase__materia__semestre=semestre)
    ).select_related("clase__materia", "clase__profesor", "salon")
    grilla = services.grilla_de(asignaciones, lambda a: f"{a.clase.materia_id} ({a.salon_id})")
    context = {
        "carreras": carreras,
        "semestres": semestres,
        "carrera": carrera,
        "semestre": semestre,
        "asignaciones": asignaciones,
        "grilla": grilla,
    }
    return render(request, "html/horario_grupo.html", context)
