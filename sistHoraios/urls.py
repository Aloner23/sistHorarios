from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path

from generator import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "",
        auth_views.LoginView.as_view(
            template_name="html/login.html", redirect_authenticated_user=True
        ),
        name="login",
    ),
    path("salir/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/generar/", views.generar, name="generar"),
    path("dashboard/reiniciar/", views.reiniciar, name="reiniciar"),
    # Profesores
    path("dashboard/profesores/", views.profesores, name="profesores"),
    path("dashboard/anadir/", views.anadirProfesor, name="anadir"),
    path("dashboard/editar/<int:idprof>", views.editarProfesor, name="editar"),
    path("dashboard/eliminar/<int:idprof>", views.eliminarProfesor, name="eliminar"),
    # Horario de un profesor y sus materias
    path("horario/<int:idprof>", views.horario, name="horario"),
    path("horario/anadir/<int:idprof>", views.anadirProfesorMateria, name="anadirProfesorMateria"),
    path(
        "horario/enter/<int:idprof>/<str:materias_clave>",
        views.enterProfesorMateria,
        name="enterProfesorMateria",
    ),
    path(
        "horario/eliminar/<str:materias_clave>/<int:idprof>",
        views.eliminarProfesorMateria,
        name="eliminarProfesorMateria",
    ),
    path("horario/<int:idprof>/<str:materias_clave>", views.asignaSalon, name="asignaSalon"),
    path(
        "horario/<int:idprof>/<str:materias_clave>/liberar",
        views.desasignar,
        name="desasignar",
    ),
    # Catálogos y vistas de horario
    path("materias/", views.materias, name="materias"),
    path("salones/", views.salones, name="salones"),
    path("salones/<str:clave>", views.horarioSalon, name="horarioSalon"),
    path("grupos/", views.horarioGrupo, name="horarioGrupo"),
]
