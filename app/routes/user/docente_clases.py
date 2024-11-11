from flask import Blueprint, redirect, render_template, request, flash, url_for
from flask_login import login_required
from app.models import Clase, AsistenciaEstudiante
from app.forms import AsistenciaEstudianteForm, BitacoraForm
from app.extensions import db

# Definir el Blueprint
docente_clases_bp = Blueprint('docente_clases', __name__)

@docente_clases_bp.route('/clase/<int:clase_id>', methods=['GET', 'POST'])
@login_required
def clase_detalle(clase_id):
    # Obtener la clase específica
    clase = Clase.query.get_or_404(clase_id)
    # Obtener las asistencias para la clase
    asistencias = AsistenciaEstudiante.query.filter_by(id_clase=clase_id).all()

    # Crear los formularios
    bitacora_form = BitacoraForm()  # Formulario para la bitácora
    asistencia_form = AsistenciaEstudianteForm()  # Formulario para la asistencia

    if request.method == 'POST':
        # Si se está enviando el formulario de bitácora
        if 'guardar_bitacora' in request.form:
            # Actualizar la bitácora de la clase
            clase.comentario_bitacora = request.form.get('comentario_bitacora', '')
            db.session.commit()
            flash('Bitácora actualizada correctamente.')

        # Si se está enviando el formulario de asistencia
        if 'guardar_asistencia' in request.form:
            # Actualizar las asistencias de los estudiantes
            for asistencia in asistencias:
                # Asignamos los campos dinámicamente usando el id de asistencia
                presencia_field = f'presencia_{asistencia.id_asistencia}'  # Campo para presencia
                justificacion_field = f'justificacion_{asistencia.id_asistencia}'  # Campo para justificación

                # Actualizar la presencia
                if presencia_field in request.form:
                    asistencia.presencia = True
                else:
                    asistencia.presencia = False

                # Actualizar la justificación si está presente
                if justificacion_field in request.form and asistencia.presencia == False:
                    asistencia.justificacion = request.form.get(justificacion_field)
                else:
                    asistencia.justificacion = None  # Si no hay justificación, se deja como None

            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('Asistencia actualizada correctamente.')

        return redirect(url_for('docente.docente_clases.clase_detalle', clase_id=clase.id_clase))

    return render_template(
        'user/clase_detalle.html', 
        clase=clase, 
        asistencias=asistencias, 
        bitacora_form=bitacora_form, 
        asistencia_form=asistencia_form
    )
