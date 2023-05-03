from django import forms
from .models import Profesores, ProfesoresHasMaterias,SalonesHasProfesoresHasMaterias

class profesorForm(forms.ModelForm):
    class Meta:
        model= Profesores
        fields='__all__'

class SalonesHasProfesoresHasMateriasForm(forms.ModelForm):
    class Meta:
        model= SalonesHasProfesoresHasMaterias
        fields='__all__'


