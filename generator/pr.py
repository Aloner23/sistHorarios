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


#funciones para la consulta de toda la base de datos
def consulta_profesores():
    cur=cnn.cursor()
    cur.execute("SELECT * FROM sistemahorario.profesores")
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
def consulta_materia():
    #acta de defuncion, cargar donde lo llevan
    #lanchita a la orilla del mar
    cur=cnn.cursor()
    cur.execute("SELECT * FROM sistemahorario.materias")
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
def consulta_salones():
    cur=cnn.cursor()
    cur.execute("SELECT * FROM sistemahorario.salones")
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
def consulta_salones_tipo(tipo):
    cur=cnn.cursor()
    sql="SELECT * FROM sistemahorario.salones where tipo='{}' ".format(tipo)
    cur.execute(sql)
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
    return datos
def consulta_salones_clave(clave):
    cur=cnn.cursor()
    sql="SELECT * FROM sistemahorario.salones where salon='{}' ".format(clave)
    cur.execute(sql)
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
    return datos
#funcion para insertar elementos a la tabla
def inserta_profesor(idProf,nombre,horario):
    cur=cnn.cursor()
    sql='''insert into sistemahorario.profesores(idProf,nombre,horario)
     values({},'{}','{}')'''.format(idProf,nombre,horario)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
def inserta_materia(Clave,nombre,horas,semestre,periodo,carrera,tipo,preferencia):
    cur=cnn.cursor()
    sql='''insert into sistemahorario.materias(Clave,nombre,horas,semestre,periodo,carrera,tipo,preferencia)
     values('{}','{}',{},{},'{}','{}','{}','{}')'''.format(Clave,nombre,horas,semestre,periodo,carrera,tipo,preferencia)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
def inserta_salon(salon,tipo,horario,lun,mar,mier,jue,vie):
    cur=cnn.cursor()
    sql='''insert into sistemahorario.salones(salon,tipo,horario,lun,mar,mier,jue,vie)
     values('{}','{}','{}','{}','{}','{}','{}','{}')'''.format(salon,tipo,horario,lun,mar,mier,jue,vie)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()

#funcion para eliminar objetos de la tabla
def eliminar_profesor(idProf):
    cur=cnn.cursor()
    sql='''DELETE FROM `sistemahorario`.`profesores` WHERE (`idProf` = '{}');'''.format(idProf)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
def eliminar_materia(Clave):
    
    cur=cnn.cursor()
    sql='''DELETE FROM `sistemahorario`.`materias` WHERE (`Clave` = '{}');'''.format(Clave)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
def eliminar_salon(salon):
    cur=cnn.cursor()
    sql='''DELETE FROM `sistemahorario`.`salones` WHERE (`salon` = '{}');'''.format(salon)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
#funcion para establecer ralacion profesor
def inserta_profesor_materia(Profesores_idProf,Materias_Clave):
    cur=cnn.cursor()
    sql='''insert into sistemahorario.profesores_has_materias(Profesores_idProf,Materias_Clave)
     values({},'{}')'''.format(Profesores_idProf,Materias_Clave)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
def insertar_profesor_materia_salon(Salon,idProf,Materia_Clave,horario):
    cur=cnn.cursor()
    sql='''  INSERT INTO
     `sistemahorario`.`salones_has_profesores_has_materias` (`Salones_salon`, `Profesores_idProf`, `Materias_Clave`, `horario`)
      VALUES ('{}', {}, '{}', '{}');'''.format(Salon,idProf,Materia_Clave,horario)
    cur.execute(sql)
    cnn.commit()
    cur.close()
    #cnn.close()
#consulta tabla completa para analisis
def consulta_analisis_preferencia(semestre,carrera,preferencia):
    cur=cnn.cursor()
    sql='''select profesores.nombre,idProf, Clave, materias.nombre, semestre,carrera,preferencia, tipo,dias,horas
    from sistemahorario.profesores, sistemahorario.materias, sistemahorario.profesores_has_materias
    where Profesores_idProf=idProf and Materias_Clave=Clave and semestre={} and carrera='{}' and preferencia='{}' '''.format(semestre,carrera,preferencia)
    cur.execute(sql)
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
    return datos
def consulta_analisis(semestre,carrera):
    cur=cnn.cursor()
    sql='''select profesores.nombre, Clave, materias.nombre, semestre,carrera,preferencia, tipo
    from sistemahorario.profesores, sistemahorario.materias, sistemahorario.profesores_has_materias
    where Profesores_idProf=idProf and Materias_Clave=Clave and semestre={} and carrera='{}' '''.format(semestre,carrera)
    cur.execute(sql)
    datos=cur.fetchall()
    for fila in datos:
        print(fila)
    cur.close()
    #cnn.close()
    return datos
#actualizacion de dias
def actualizaDia(dia,hora,salon):
    cur=cnn.cursor()
    sql='''UPDATE `sistemahorario`.`salones` SET `{}` = '{}' WHERE (`salon` = '{}');'''.format(dia,hora,salon)
    cur.execute(sql)
    cnn.commit()
    cur.close()

#funcion para medir promedios de preferencias
def promedios(datos):
    t=0
    n=0
    m=0
    for fila in datos:
        if fila[5] =='Tarde':
            t=t+1
        elif fila[5] =='Noche' :
            n=n+1
        else:
            m=m+1
    dict={'Manana':m,'Tarde':t,'Noche':n}
    lst=[m,t,n]
    return dict
def preferenciaPuntos(preferencia):
    if preferencia == 'Manana':
        puntos=0
    if preferencia == 'Tarde':
        puntos=11
    if preferencia == 'Noche':
        puntos=21
    return puntos
def cambiar_hora_salon():
    b=0

def depurador_hora_salon(preferencia,tipo):
    #se necesita un minimo de 2 horas para entrar al bloquev
    salon=consulta_salones_tipo(tipo)
    newsalon=[]
    diasDisp=[]
    for tupla in salon:
        string=tupla[2]
        rango=0
        numAux=0
        b=0
        a=0
        cont=1
        tieneAlmenosUna=False
        auxSave=[tupla[0],0,0,0,0,0]
        for string in tupla[2:7]:
            
            for i in string:
                #se necesita usar una pila
                if i==',':
                    #se hace un pop de la pila y se resuelve la operacion
                    #para ver si el bloque esta en la preferencia
                    if preferenciaPuntos(preferencia)>=a and b>preferenciaPuntos(preferencia):
                        tieneAlmenosUna=True
                        auxSave[cont]=1
                        #cont=cont+1
                        #print("...............")
                        #print(cont)
                        #print(a)
                        #print(b)
                        rango=0
                        numAux=0
                        #newsalon.append([tupla[0],lun,mart,mier,juev,vier])
                    elif preferenciaPuntos(preferencia)<a and a <(preferenciaPuntos(preferencia)+10):
                        tieneAlmenosUna=True
                        auxSave[cont]=1
                        #cont=cont+1
                        #print("...............")
                        #print(cont)
                        #print(a)
                        #print(b)
                        rango=0
                        numAux=0
                        #newsalon.append([tupla[0],lun,mart,mier,juev,vier])
                    else:
                    #cont=cont+1
                        rango=0
                        numAux=0
                if i=='-':
                    numAux=0
                    rango=1
                elif rango==0 and numAux==0 and i!=',' and i!='-' and i!='x':
                    a=int(i)
                    numAux=1
                elif rango==0 and numAux==1:
                    a=int(a)*10+int(i)
                elif rango!=0 and numAux==0 and i!=',' and i!='-' and i!='x':
                    b=int(i)
                    numAux=1
                elif rango!=0 and numAux==1:
                    b=int(b)*10+int(i)

            cont=cont+1
        if tieneAlmenosUna == True:
                newsalon.append(auxSave)
                tieneAlmenosUna = False
                auxSave=[tupla[0],0,0,0,0,0]
        else:
            auxSave=[tupla[0],0,0,0,0,0]
        cont=1            
    rep=newsalon           
    return rep

#estas trabajando en esta parte
def asignacionHorario(salones,horas,preferencia):
    dias=[]
    horario=''
    countI=2
    for tupla in salones:
        for i in tupla[1:5]:
            if i == 1:
                salon=consulta_salones_clave(tupla[0])
                horarioNSalon,ap,bp= modificadorSalon(horas,salon[0][countI],preferencia)
                horario=modificadorClase(horas,ap)
                if countI==2:
                    dias='Lun,Mier'
                if countI==3:
                    dias='Mart,Juev'
                break
            countI=countI+1
    if countI==2:
        actualizaDia('lun',horarioNSalon,salon[0][0])
        actualizaDia('mier',horarioNSalon,salon[0][0])
    if countI==3:
        actualizaDia('mar',horarioNSalon,salon[0][0])
        actualizaDia('jue',horarioNSalon,salon[0][0])
    return [salon[0][0],horarioNSalon,horario,dias]
def modificadorClase(horas,ap):
    bNuevo=ap+(horas*2)
    horario=str(str(ap)+'-'+str(bNuevo)+',')
    return horario
def modificadorSalon(horas,horario,preferencia):
    elimino=False
    point=0
    rango=0
    numAux=0
    b=0
    a=0

    aManana=0
    bManana=0

    aTarde=0
    bTarde=0

    aNoche=0
    bNoche=0

    ap=0
    bp=0

    cuentaSec=1
    for i in horario:
        if i=='-':
                numAux=0
                rango=1
        elif i==',':
            rango=0
            numAux=0
            if preferenciaPuntos(preferencia)>=a and b>preferenciaPuntos(preferencia):
                        ap=a
                        bp=b
                        if (b-a)<horas*2:
                            elimino=True
                            #bp=ap+(horas*2)
                        if cuentaSec==1:
                            aManana=a
                            bManana=b
                        elif cuentaSec==2:
                            aTarde=a
                            bTarde=b
                        elif cuentaSec==3:
                            aNoche=a
                            bNoche=b
                        point=cuentaSec
                        cuentaSec=cuentaSec+1
            elif preferenciaPuntos(preferencia)<a and a <(preferenciaPuntos(preferencia)+10):
                        rango=0
                        numAux=0
                        ap=a
                        bp=b
                        if (b-a)<horas*2:
                            elimino=True
                            #bp=ap+(horas*2)
                        if cuentaSec==1:
                            aManana=a
                            bManana=b
                        elif cuentaSec==2:
                            aTarde=a
                            bTarde=b
                        elif cuentaSec==3:
                            aNoche=a
                            bNoche=b
                        point=cuentaSec
                        cuentaSec=cuentaSec+1
            else:
                if cuentaSec==1:
                            rango=0
                            numAux=0
                            aManana=a
                            bManana=b
                elif cuentaSec==2:
                            rango=0
                            numAux=0
                            aTarde=a
                            bTarde=b
                elif cuentaSec==3:
                            aNoche=a
                            bNoche=b
                cuentaSec=cuentaSec+1
        elif rango==0 and numAux==0 and i!=',' and i!='-'and i!='x':
                a=int(i)
                numAux=1
        elif rango==0 and numAux==1:
                a=int(a)*10+int(i)
        elif rango!=0 and numAux==0 and i!=',' and i!='-'and i!='x':
                b=int(i)
                numAux=1
        elif rango!=0 and numAux==1:
                b=int(b)*10+int(i)
        

    aNuevo=ap+(horas*2)
    #horario=str(str(aNuevo)+'-'+str(b)+',')
    if elimino==True:
        if preferencia=='Manana':
            horario=str('x'+','+str(aNuevo)+'-'+str(bTarde)+','+str(aNoche)+'-'+str(bNoche)+',')
        elif preferencia=='Tarde':
            horario=str(str(aManana)+'-'+str(bManana)+','+'x'+','+str(aNuevo)+'-'+str(bNoche)+',')
        elif preferencia=='Noche':
            horario=str(str(aManana)+'-'+str(bManana)+','+str(aTarde)+'-'+str(bTarde)+','+'x'+',')
    else:
        if preferencia=='Manana':
            horario=str(str(aNuevo)+'-'+str(bManana)+','+str(aTarde)+'-'+str(bTarde)+','+str(aNoche)+'-'+str(bNoche)+',')
        elif preferencia=='Tarde':
            horario=str(str(aManana)+'-'+str(bManana)+','+str(aNuevo)+'-'+str(bTarde)+','+str(aNoche)+'-'+str(bNoche)+',')
        elif preferencia=='Noche':
            horario=str(str(aManana)+'-'+str(bManana)+','+str(aTarde)+'-'+str(bTarde)+','+str(aNuevo)+'-'+str(bNoche)+',')

    
    return horario,ap,bp
    
def convertidorMatriz(matriz,a,b,dias):
    intdia=0
    if dias=='Mart,Juev':
        intdia=1
    i=a-1
    while i<b:
        matriz[intdia][i]=1
        matriz[intdia+2][i]=1
    return matriz

def algoritmo(semestre,carrera):
    datos=consulta_analisis(semestre,carrera)
    lst=promedios(datos)
    #aqui se necesita de un order by min-max
    #aqui va el for que recorre cada preferencia
    for preferencia in lst:
        #ejemplo, noche,manana,tarde
        #---aqui va el for  de cada bloque de preferencias cada query---
        #se selecciona el bloque profesor materia a asignar
        print(semestre)
        print(carrera)
        print(preferencia)

        #si no encuenntra ningunprofesor_materia con esa preferencia lo salta
        datosProfMat= consulta_analisis_preferencia(semestre,carrera,preferencia)

        if len(datosProfMat)!=0:
            #selecciona para asignar a un salon
            #horas/dias
            for clases in datosProfMat:
                preferencia=clases[6]
                tipo=clases[7]
                print(preferencia)
                salones=depurador_hora_salon(preferencia,tipo)
                print (salones)
                print('-------------------------')
                horasN=int(clases[9]/clases[8])
                print(horasN)
                secuencia= asignacionHorario(salones,horasN,preferencia)
                print(secuencia)

    return secuencia


#algoritmo de asignacion de salon
#consulta_profesores()
#consulta_materia()
#consulta_salones()
#inserta_profesor(7,'Bernardo','Tiempo completo','Tarde')
#inserta_materia('COM99101','Metodologia',4,3,'P','Computacion')
#inserta_salon('LI-Pace','Computadoras','7:00 -13:00','x','x','x','x','x')
#eliminar_profesor(7)
#eliminar_materia('COM99101')
#eliminar_salon('LI-Pace')
#inserta_profesor_materia(1,'COM11101')
#inserta_profesor_materia(2,'COM16303')
#inserta_profesor_materia(3,'COM12103')
#inserta_profesor_materia(4,'COM11107')
#inserta_profesor_materia(5,'COM23101')
#inserta_profesor_materia(1,'COM11102')
#inserta_profesor_materia(2,'COM11103')
#inserta_profesor_materia(3,'COM12101')
#9
#inserta_profesor_materia(4,'COM12102')
#consulta_analisis_preferencia(1,'Comun','Tarde')
#consulta_analisis(1,'Computacion')
#salones=consulta_salones_tipo('Butaca')
#print(salones[0][1])
#depurador_hora_salon('Manana','Butaca')
#ls=depurador_hora_salon('Noche','Computadora')
#ls=depurador_hora_salon('Manana','Computadora')
#ls2=depurador_hora_salon('Tarde','Computadora')
#print(ls)
#ls3=depurador_hora_salon('Noche','Computadora')

#res=algoritmo(8,'Computacion')  



#datosProfMat= consulta_analisis_preferencia(1,'Comun','Tarde')
#print(datosProfMat[0][6])
#----------------------------------------------------------------------------------------------------------------

#salones=depurador_hora_salon('Noche','Computadora')
#salones=sorted(salones, key=itemgetter(1))
#print('-------------------------')
#print (salones)
#print('-------------------------')


#secuencia= asignacionHorario(salones,2,'Noche')
#print(secuencia)

#------------------------------------------------------------------------------------------------------------
#resp=asignacionHorario(salones,'Manana',2)
#print("----------------------------")
#print(resp)

#hora=modificadorClase(2,'20-30,')
#print(hora)
"""
print('Horario:')
hora,ap,bp=modificadorSalon(2,'0-10,11-20,21-30,','Manana')
print(hora)
h=modificadorClase(2,ap)
print('Hora de clase:')
print(h)
hora,ap,bp=modificadorSalon(2,hora,'Manana')
print('Horario:')
print(hora)
h=modificadorClase(2,ap)
print('Hora de clase:')
print(h)
hora,ap,bp=modificadorSalon(2,hora,'Manana')
print('Horario:')
print(hora)
h=modificadorClase(2,ap)
print('Hora de clase:')
print(h)
print('---------Quitamos la hora de la tarde-------------')
hora,ap,bp=modificadorSalon(2,hora,'Tarde')
print(hora)
hora,ap,bp=modificadorSalon(2,hora,'Tarde')
print(hora)
hora,ap,bp=modificadorSalon(2,hora,'Tarde')
print(hora)
hora,ap,bp=modificadorSalon(2,hora,'Noche')
print(hora)
"""

#h=modificadorClase(2,ap)
#print(h)

#hca
#algorit y comp
#computacion1
#atin -admins conta
#inteligencia de negocio
