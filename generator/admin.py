from django.contrib import admin

from .models import Asignacion, Materia, Profesor, ProfesorMateria, Salon


class ProfesorMateriaInline(admin.TabularInline):
    model = ProfesorMateria
    extra = 0
    autocomplete_fields = ["materia"]


@admin.register(Profesor)
class ProfesorAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre", "correo", "horario"]
    search_fields = ["nombre", "correo"]
    inlines = [ProfesorMateriaInline]


@admin.register(Materia)
class MateriaAdmin(admin.ModelAdmin):
    list_display = [
        "clave",
        "nombre",
        "carrera",
        "semestre",
        "horas",
        "dias",
        "tipo",
        "preferencia",
    ]
    list_filter = ["carrera", "semestre", "tipo", "preferencia"]
    search_fields = ["clave", "nombre"]


@admin.register(Salon)
class SalonAdmin(admin.ModelAdmin):
    list_display = ["clave", "tipo", "lun", "mar", "mier", "jue", "vie"]
    list_filter = ["tipo"]
    search_fields = ["clave"]


@admin.register(Asignacion)
class AsignacionAdmin(admin.ModelAdmin):
    list_display = ["clase", "salon", "dias", "horario"]
    list_filter = ["dias", "salon"]
    list_select_related = ["clase__profesor", "clase__materia", "salon"]
