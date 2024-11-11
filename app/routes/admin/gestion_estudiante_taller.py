from flask import Blueprint, jsonify, render_template, redirect, url_for, request, flash
from flask_login import login_required
from app.models import Estudiantes, Taller, EstudianteTaller
from app.extensions import db
from app.routes.admin.decorators import admin_required
from app.forms import EstudianteTallerForm

# Crear el Blueprint
estudiantes_taller_bp = Blueprint('estudiantes_taller_admin', __name__)

# Rutas


@estudiantes_taller_bp.route('/', methods=['GET', 'POST'], endpoint='estudiantes_taller_admin_gestionar')
@login_required
@admin_required
def gestionar_estudiantes_taller():
    form = EstudianteTallerForm()

    if request.method == 'POST':
        taller_id = request.form.get('taller_id')
        id_estudiantes = request.form.getlist('id_estudiantes[]')  # Obtener todos los estudiantes seleccionados

        if not taller_id or not id_estudiantes:
            flash('Debe seleccionar un taller y al menos un estudiante.', 'warning')
            return redirect(url_for('admin.estudiantes_taller_admin.estudiantes_taller_admin_gestionar'))

        # Iterar sobre los estudiantes seleccionados
        for id_estudiante in id_estudiantes:
            # Verificar si ya existe la asignación
            asignacion_existente = EstudianteTaller.query.filter_by(
                id_estudiante=id_estudiante,
                taller_id=taller_id
            ).first()

            if not asignacion_existente:
                nueva_asignacion = EstudianteTaller(
                    id_estudiante=id_estudiante,
                    taller_id=taller_id
                )
                db.session.add(nueva_asignacion)

        # Guardar los cambios en la base de datos
        db.session.commit()
        flash('Estudiantes asignados correctamente al taller', 'success')
        return redirect(url_for('admin.estudiantes_taller_admin.estudiantes_taller_admin_gestionar'))

    # Consultar todos los estudiantes y talleres para renderizar en el formulario
    estudiantes = Estudiantes.query.all()
    talleres = Taller.query.all()

    return render_template('admin/estudiantes_taller.html', estudiantes=estudiantes, talleres=talleres, form=form)

@estudiantes_taller_bp.route('/delete/<int:id_taller_estudiante>', methods=['POST'], endpoint='estudiantes_taller_admin_delete')
@login_required
@admin_required
def delete_estudiante_taller(id_taller_estudiante):
    asignacion = EstudianteTaller.query.get_or_404(id_taller_estudiante)
    db.session.delete(asignacion)
    db.session.commit()
    flash('Asignación eliminada correctamente', 'success')
    return redirect(url_for('admin.estudiantes_taller_admin.estudiantes_taller_admin_gestionar'))


@estudiantes_taller_bp.route('/load_students/<int:taller_id>', methods=['GET'])
@login_required
@admin_required
def load_students(taller_id):
    asignaciones = EstudianteTaller.query.filter_by(taller_id=taller_id).all()
    estudiantes_asignados = [
        {
            'id_estudiante': asignacion.id_estudiante,
            'nombre': asignacion.estudiante.nombre,
            'apellido_paterno': asignacion.estudiante.apellido_paterno,
            'apellido_materno': asignacion.estudiante.apellido_materno,
            'rut_estudiante': asignacion.estudiante.rut_estudiante,
            'curso': asignacion.estudiante.curso
        } for asignacion in asignaciones
    ]
    
    return render_template('admin/estudiantes_list.html', estudiantes_asignados=estudiantes_asignados)
