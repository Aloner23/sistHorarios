from django.shortcuts import render
from django.shortcuts import render,redirect

from .models import Materias, Profesores, Salones, ProfesoresHasMaterias, SalonesHasProfesoresHasMaterias
from .forms import profesorForm, SalonesHasProfesoresHasMateriasForm

from tokenize import Double
import pymysql
import operator
from operator import itemgetter


#se presentan los metos basicos de consulta, eliminar e insertar

#aqui se prepara la coneccion a la BD
cnn=pymysql.connect(host="localhost",user="root",
passwd="sqladmin",database="sistemahorario")
cnn1=pymysql.connect(host="localhost",user="root",
passwd="sqladmin",database="sistemahorario")

# Create your views here.
def login(request):
    return render(request,'html/login.html')
def base(request):
    return render(request,'html/base.html')
def profesores(request):
    profes= Profesores.objects.all()
    return render(request,'html/profesores.html',{'profes':profes})

def materias(request):
    materias=Materias.objects.all()
    return render (request,'html/materias.html',{'materias':materias})
def salones(request):
    salones=Salones.objects.all()
    return render (request,'html/salones.html',{'salones':salones})

def horario(request,idprof):
    profesor=Profesores.objects.get(idprof=idprof)
    materias=ProfesoresHasMaterias.objects.raw('SELECT * FROM sistemahorario.profesores_has_materias where Profesores_idProf=%s',[idprof])
    horario=SalonesHasProfesoresHasMaterias.objects.raw('SELECT * FROM sistemahorario.salones_has_profesores_has_materias where Profesores_idProf=%s',[idprof])
    horas=["7:00","7:30","8:00","8:30","9:00","9:30","10:00","10:30","11:00","11:30","12:00","12:30",
    "13:00","13:30","14:00","14:30","15:00","15:30","16:00","16:30","17:00","17:30","18:00","18:30","19:00",
    "19:30","20:00","20:30","21:00","21:30","22:00"]

    hr=[
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0},
    {"Lun":0,"Mar":0,"Mie":0,"Juev":0,"Vier":0}]
    stat=[]
    def status(horario,materias):
        for i in materias:
            flag=False
            for y in horario:
                if i.materias_clave== y.materias_clave:
                    stat.append("Asignado")
                    flag= True
            if flag== False:
                stat.append("N/A")
        
        return stat
    stat=status(horario,materias)
    compl2=zip(materias,stat)
    def convertidor(horario,hr):
        count=''
        for y in horario:
            count=''
            a=0
            b=0
            con=0
            for i in y.horario:
                if i=='-':
                    a=int(count)
                    count=''
                else:
                    count=count+i
            b=int(count)
            con=0
            for x in hr:
                if con<=b and con>=a:
                    if y.dias==1:
                        x['Lun']=y.materias_clave.clave
                        x['Mie']=y.materias_clave.clave
                    if y.dias==2:
                        x['Mar']=y.materias_clave.clave
                        x['Juev']=y.materias_clave.clave
                    con=con+1
                else:
                    con=con+1
        return hr
    rend= convertidor (horario,hr)
    compl=zip(horas,rend)
    
    context ={
        'profesor':profesor,
        'materias':materias,
        'horario':horario,
        'horas':horas,
        'rend':rend,
        'compl':compl,
        'compl2':compl2,
    }
    
    return render (request,'html/horario.html',context)

def editarProfesor(request,idprof):
    profesor=Profesores.objects.get(idprof=idprof)
    form = profesorForm(request.POST or None, request.FILES or None, instance=profesor)
    if form.is_valid():
        form.save()
        return redirect('/dashboard/profesores/')
    return render(request,'html/form.html',{'form':form})
def anadirProfesor(request):
    form = profesorForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('/dashboard/profesores/')
    return render(request,'html/form.html',{'form':form})
def eliminarProfesor(request,idprof):
    profesor=Profesores.objects.get(idprof=idprof)
    profesor.delete()
    return redirect('/dashboard/profesores/')
def anadirProfesorMateria(request,idprof):
    profesor=Profesores.objects.get(idprof=idprof)
    materias=Materias.objects.all()
    context={
        "profesor":profesor,
        "materias":materias
    }
    return render(request,'html/asignaMateria.html',context)
"""
def enterProfesorMateria(request,idprof):
    materias_clave = request.GET.get('input_value_1')
    cur=cnn.cursor()
    sql='''insert into sistemahorario.profesores_has_materias(Profesores_idProf,Materias_Clave)
     values({},'{}')'''.format(idprof,materias_clave)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
    return redirect('/horario/'+str(idprof))
"""
def enterProfesorMateria(request,idprof,materias_clave):
    cur=cnn.cursor()
    sql='''insert into sistemahorario.profesores_has_materias(Profesores_idProf,Materias_Clave)
     values({},'{}')'''.format(idprof,materias_clave)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
    return redirect('/horario/'+str(idprof))

def eliminarProfesorMateria(request,materias_clave,idprof):
    cur=cnn.cursor()
    sql='''DELETE FROM `sistemahorario`.`profesores_has_materias` WHERE (`Profesores_idProf` = '{}') and (`Materias_Clave` = '{}');'''.format(idprof,materias_clave)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
    return redirect('/horario/'+str(idprof))

def asignaSalon(request,idprof,materias_clave):
    profesor=Profesores.objects.get(idprof=idprof)
    materia=Materias.objects.get(clave=materias_clave)
    salones=Salones.objects.all()
    context ={
        'salones':salones,
        'profesor':profesor,
        'materia':materia
    }
    return render(request,'html/asignaSalon.html',context)

"""

def anadirProfesorMateriaSalon(request,idprof,materias_clave,salon):
    profesor=Profesores.objects.get(idprof=idprof)
    materia=Materias.objects.get(clave=materias_clave)
    salon=Salones.objects.get(salon=salon)

    #relacion=SalonesHasProfesoresHasMaterias(salones_salon = salon,profesores_idprof = profesor,materias_clave = materia)
    #relacion.save()
    context={
    'profesor':profesor,
    'materia':materia,
    'salon':salon
    }
    return render(request,'html/formSalA.html',context)
"""

def anadirProfesorMateriaSalon(request):
    form = SalonesHasProfesoresHasMateriasForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('/dashboard/profesores/')
    return render(request,'html/form.html',{'form':form})

def submitPMS(request,idprof,materias_clave,salon):
    profesor=Profesores.objects.get(idprof=idprof)
    materia=Materias.objects.get(clave=materias_clave)
    salon=Salones.objects.get(salon=salon)
    horaInicio=request.GET["horaI"]
    horaSalida=request.GET["horaS"]
    lunes=request.GET["Lunes"]
    martes=request.GET["Martes"]
    miercoles=request.GET["Miercoles"]
    jueves=request.GET["Jueves"]
    viernes=request.GET["Viernes"]
    context={
        "horaInicio":horaInicio,
        "horaSalida":horaSalida,
        "lunes":lunes,
        "martes":martes,
        "miercoles":miercoles,
        "jueves":jueves,
        "viernes":viernes,
        "salon":salon,
        "materia":materia,
        "profesor":profesor
    }


    return render(request,'html/prueba.html',context)