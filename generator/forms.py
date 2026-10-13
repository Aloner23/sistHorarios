from django import forms

from . import scheduler
from .models import Asignacion, Dias, Profesor, Salon

HORAS_CHOICES = [(i, scheduler.etiqueta_hora(i)) for i in range(scheduler.TOTAL_MEDIAS_HORAS + 1)]


class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ["nombre", "correo", "horario"]


class GenerarForm(forms.Form):
    carrera = forms.ChoiceField(required=False)
    semestre = forms.TypedChoiceField(required=False, coerce=int, empty_value=None)

    def __init__(self, *args, carreras=(), semestres=(), **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["carrera"].choices = [("", "Todas")] + [(c, c) for c in carreras]
        self.fields["semestre"].choices = [("", "Todos")] + [(s, f"{s}°") for s in semestres]


class AsignacionForm(forms.ModelForm):
    """Asignación manual de una clase a un salón (reemplaza al flujo
    ``asignaSalon`` → ``formTodo`` → ``submitPMS`` que nunca guardaba nada)."""

    inicio = forms.TypedChoiceField(choices=HORAS_CHOICES[:-1], coerce=int, label="Hora de inicio")
    fin = forms.TypedChoiceField(choices=HORAS_CHOICES[1:], coerce=int, label="Hora de salida")

    class Meta:
        model = Asignacion
        fields = ["salon", "dias", "inicio", "fin"]

    def __init__(self, *args, clase, **kwargs):
        super().__init__(*args, **kwargs)
        self.clase = clase
        self.instance.clase = clase
        materia = clase.materia
        self.fields["salon"].queryset = Salon.objects.filter(tipo=materia.tipo)
        codigos = scheduler.OPCIONES_POR_SESIONES.get(materia.dias, ())
        self.fields["dias"].choices = [(c, Dias(c).label) for c in codigos]
        if not self.is_bound and not self.instance.pk:
            self.initial["fin"] = materia.medias_horas_por_sesion

    def clean(self):
        from .services import conflictos

        datos = super().clean()
        salon, dias = datos.get("salon"), datos.get("dias")
        inicio, fin = datos.get("inicio"), datos.get("fin")
        if salon and dias and inicio is not None and fin is not None:
            for error in conflictos(self.clase, salon, dias, inicio, fin):
                self.add_error(None, error)
        return datos
