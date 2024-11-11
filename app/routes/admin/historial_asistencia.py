from io import BytesIO
from flask import Blueprint, render_template, redirect, send_file, url_for, request, flash
from flask_login import login_required
from sqlalchemy import func , Float , cast
from ...models import Estudiantes, Clase, AsistenciaEstudiante, Taller, EstudianteTaller, db
from ...forms import AsistenciaEstudianteForm
import logging
import pandas as pd
from flask import Blueprint, render_template
from datetime import datetime
import calendar
from app import cache 

# Inicializar el blueprint
historial_bp = Blueprint('historial_admin', __name__)

# Configurar logging para depuración
logging.basicConfig(level=logging.DEBUG)

@historial_bp.route('/', methods=['GET'], endpoint='seleccionar_taller')
@login_required
def seleccionar_taller():
    """Ruta para seleccionar un taller antes de ver el historial de asistencia."""
    talleres = Taller.query.all()
    return render_template('admin/seleccionar_taller.html', talleres=talleres)

@historial_bp.route('/taller/<int:taller_id>', methods=['GET', 'POST'], endpoint='historial_asistencia')
@login_required
def historial_asistencia(taller_id):
    """Ruta para mostrar y actualizar el historial de asistencia de un taller específico."""
    taller = Taller.query.get_or_404(taller_id)
    clases = Clase.query.filter_by(taller_id=taller_id).all()
    estudiantes = Estudiantes.query.join(EstudianteTaller).filter_by(taller_id=taller_id).all()
    form = AsistenciaEstudianteForm()

    # Manejo de POST para actualizar asistencias
    if request.method == 'POST':
        for clase in clases:
            for estudiante in estudiantes:
                presencia_key = f'asistencia_{estudiante.id_estudiante}_{clase.id_clase}'
                justificacion_key = f'justificacion_{estudiante.id_estudiante}_{clase.id_clase}'
                presencia = request.form.get(presencia_key) == 'on'
                justificacion = request.form.get(justificacion_key)

                asistencia = AsistenciaEstudiante.query.filter_by(
                    id_clase=clase.id_clase, id_estudiante=estudiante.id_estudiante
                ).first()

                if asistencia:
                    asistencia.presencia = presencia
                    asistencia.justificacion = justificacion if not presencia else None
                else:
                    nueva_asistencia = AsistenciaEstudiante(
                        id_clase=clase.id_clase,
                        id_estudiante=estudiante.id_estudiante,
                        presencia=presencia,
                        justificacion=justificacion if not presencia else None
                    )
                    db.session.add(nueva_asistencia)

        try:
            db.session.commit()
            flash('Asistencia actualizada correctamente.')
        except Exception as e:
            db.session.rollback()
            flash(f'Ocurrió un error al guardar la asistencia: {e}', 'error')

        return redirect(url_for('admin.historial_admin.historial_asistencia', taller_id=taller_id))

    asistencia_dict = {}
    porcentaje_asistencia = {}

    for estudiante in estudiantes:
        total_clases = len(clases)
        clases_asistidas = 0

        for clase in clases:
            asistencia = AsistenciaEstudiante.query.filter_by(
                id_clase=clase.id_clase, id_estudiante=estudiante.id_estudiante
            ).first()

            if estudiante.id_estudiante not in asistencia_dict:
                asistencia_dict[estudiante.id_estudiante] = {}

            asistencia_dict[estudiante.id_estudiante][clase.id_clase] = asistencia.presencia if asistencia else False

            if asistencia and asistencia.presencia:
                clases_asistidas += 1

        porcentaje_asistencia[estudiante.id_estudiante] = (clases_asistidas / total_clases * 100) if total_clases > 0 else 0

    return render_template(
        'admin/historial_asistencia.html', 
        form=form, 
        taller=taller, 
        clases=clases, 
        estudiantes=estudiantes, 
        asistencia_dict=asistencia_dict, 
        porcentaje_asistencia=porcentaje_asistencia
    )

@historial_bp.route('/exportar/taller/<int:taller_id>')
@login_required
def exportar_historial_por_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    nombre_taller = taller.nombre.replace(" ", "_")
    clases = Clase.query.filter_by(taller_id=taller_id).order_by(Clase.fecha).all()
    estudiantes = Estudiantes.query.join(EstudianteTaller).filter_by(taller_id=taller.taller_id).all()

    data = []
    for estudiante in estudiantes:
        row = {'Estudiante': f"{estudiante.nombre} {estudiante.apellido_paterno}"}
        clases_asistidas = 0
        total_clases = len(clases)

        for clase in clases:
            fecha_clase = clase.fecha.strftime('%Y-%m-%d')
            asistencia = AsistenciaEstudiante.query.filter_by(
                id_clase=clase.id_clase,
                id_estudiante=estudiante.id_estudiante
            ).first()

            if asistencia and asistencia.presencia:
                row[fecha_clase] = 1
                clases_asistidas += 1
            else:
                row[fecha_clase] = 0

        porcentaje_asistencia = (clases_asistidas / total_clases * 100) if total_clases > 0 else 0
        row['Porcentaje Asistencia'] = round(porcentaje_asistencia, 2)
        data.append(row)

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f"Asistencia_{taller.nombre}")

    output.seek(0)
    return send_file(
        output,
        download_name=f"historial_{nombre_taller}.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

#Informe General
@historial_bp.route('/exportar_informe_general')
@login_required
def exportar_informe_general():
    talleres = Taller.query.all()
    
    # Crear una lista de meses de marzo a diciembre
    meses = [datetime(2024, m, 1).strftime('%B %Y') for m in range(3, 13)]
    
    # Diccionario para almacenar los porcentajes de asistencia por taller y por mes
    asistencia_por_taller = {}

    # Procesar datos para cada taller
    for taller in talleres:
        asistencia_por_taller[taller.nombre] = {mes: 0.0 for mes in meses}  # Inicializar con 0% para todos los meses
        
        # Obtener todas las clases del taller
        clases = Clase.query.filter_by(taller_id=taller.taller_id).all()
        
        # Calcular porcentaje de asistencia por mes
        for clase in clases:
            mes_nombre = clase.fecha.strftime('%B %Y')
            if mes_nombre in asistencia_por_taller[taller.nombre]:
                total_estudiantes = EstudianteTaller.query.filter_by(taller_id=taller.taller_id).count()
                asistencias = AsistenciaEstudiante.query.filter_by(id_clase=clase.id_clase).all()
                presentes = sum(1 for a in asistencias if a.presencia)
                if total_estudiantes > 0:
                    porcentaje = (presentes / total_estudiantes) * 100
                    asistencia_por_taller[taller.nombre][mes_nombre] = round(porcentaje, 2)

    # Preparar los datos para el DataFrame de pandas
    data = []
    for taller, meses_data in asistencia_por_taller.items():
        row = {"Taller": taller}
        row.update(meses_data)
        data.append(row)

    # Crear DataFrame
    df = pd.DataFrame(data)
    
    # Generar archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Informe General')

    # Resetear el puntero del archivo a inicio
    output.seek(0)

    # Enviar el archivo Excel como respuesta
    return send_file(
        output,
        download_name="informe_general_asistencia.xlsx",
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@historial_bp.route('/informe_general')
@login_required
def informe_general():
    # Obtener la lista de talleres y los meses de marzo a diciembre
    talleres = Taller.query.all()
    meses = [datetime(2024, m, 1).strftime('%B %Y') for m in range(3, 13)]

    # Consulta para obtener los porcentajes de asistencia por taller y por mes
    resultados = (
        db.session.query(
            Taller.nombre.label("taller_nombre"),
            func.date_format(Clase.fecha, '%M %Y').label("mes"),
            (func.sum(cast(AsistenciaEstudiante.presencia, Float)) / func.count(AsistenciaEstudiante.id_estudiante) * 100).label("porcentaje")
        )
        .join(Clase, Clase.taller_id == Taller.taller_id)
        .join(AsistenciaEstudiante, AsistenciaEstudiante.id_clase == Clase.id_clase)
        .group_by(Taller.nombre, func.date_format(Clase.fecha, '%M %Y'))
        .all()
    )

    # Inicializar diccionario para almacenar asistencia por taller y mes
    asistencia_por_taller = {taller.nombre: {mes: 0.0 for mes in meses} for taller in talleres}

    # Poblar el diccionario con los resultados de la consulta
    for resultado in resultados:
        taller_nombre = resultado.taller_nombre
        mes = resultado.mes
        porcentaje = resultado.porcentaje
        if mes in asistencia_por_taller[taller_nombre]:
            asistencia_por_taller[taller_nombre][mes] = round(porcentaje, 2)

    return render_template(
        'admin/informe_general.html',
        meses=meses,
        asistencia_por_taller=asistencia_por_taller
    )