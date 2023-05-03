"""sistHoraios URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from generator import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", views.base),
    path("dashboard/profesores/", views.profesores),
    path("materias/", views.materias),
    path("horario/<int:idprof>", views.horario, name='horario'),
    path("salones/", views.salones),
    path("dashboard/editar/<int:idprof>",views.editarProfesor, name='editar'),
    path("dashboard/eliminar/<int:idprof>",views.eliminarProfesor, name='eliminar'),
    path("horario/eliminar/<str:materias_clave>/<int:idprof>",views.eliminarProfesorMateria, name='eliminarProfesorMateria'),
    path("horario/anadir/<int:idprof>",views.anadirProfesorMateria, name='anadirProfesorMateria'),
    path("horario/enter/<int:idprof>/<str:materias_clave>", views.enterProfesorMateria,name='enterProfesorMateria'),
    path("dashboard/anadir/",views.anadirProfesor, name='anadir'),
    #path("horario/<int:idprof>/<str:materias_clave>/<str:salon>",views.anadirProfesorMateriaSalon, name='anadirPMS'),
    path("horario/inserta",views.anadirProfesorMateriaSalon, name='anadirPMS'),
    path("submitPMS/<int:idprof>/<str:materias_clave>/<str:salon>",views.submitPMS, name='submitPMS'),
    #path("dashboard/asigna/",views.asignaSalon, name='asignaSalon'),
    path("horario/<int:idprof>/<str:materias_clave>",views.asignaSalon, name='asignaSalon'),
    path("",views.login)
]
