from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Planificacion, Taller
from app.extensions import db
from app.forms import PlanificacionForm

# Crear el Blueprint para las rutas de Planificación de docentes
planificacion_bp = Blueprint('planificacion_docente', __name__)

# Ruta para listar las planificaciones del docente
@planificacion_bp.route('/')
@login_required
def listar_planificaciones_docente():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    planificaciones = Planificacion.query.filter(
        Planificacion.taller_id.in_([t.taller_id for t in talleres])).all()

    # Selecciona el primer taller como el taller actual por defecto si existe
    selected_taller = talleres[0] if talleres else None

    # Genera el estado de los meses
    estados = {}
    meses = ['Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre']
    for mes in meses:
        planificacion_mes = next((p for p in planificaciones if p.mes == mes), None)
        if planificacion_mes:
            if all([planificacion_mes.habilidades, planificacion_mes.recursos, planificacion_mes.actividades]):
                estados[mes] = 'Planificada'
            else:
                estados[mes] = 'En proceso'
        else:
            estados[mes] = 'No realizado'

    # Renderiza el template con el taller seleccionado
    return render_template('user/docente_planificaciones.html', 
                           talleres=talleres, 
                           planificaciones=planificaciones, 
                           estados=estados, 
                           selected_taller=selected_taller,
                           meses=meses)

# Ruta para que el docente pueda definir o editar el objetivo general del taller
@planificacion_bp.route('/talleres/<int:id>/editar_objetivo', methods=['GET', 'POST'])
@login_required
def editar_objetivo_taller_docente(id):
    form = PlanificacionForm()
    taller = Taller.query.filter_by(taller_id=id, id_docente=current_user.id_docente).first_or_404()

    if form.validate_on_submit():  # Validación del formulario
        taller.objetivo_general = form.objetivo_general.data
        db.session.commit()
        flash('Objetivo general actualizado exitosamente')
        return redirect(url_for('planificacion_docente.listar_planificaciones_docente'))

    form.objetivo_general.data = taller.objetivo_general  # Cargar datos en el formulario
    return render_template('user/editar_objetivo.html', taller=taller, form=form)

# Ruta para crear una nueva planificación desde la perspectiva del docente
@planificacion_bp.route('/<int:taller_id>/nueva', methods=['GET', 'POST'])
@login_required
def planificacion_taller_docente(taller_id):
    form = PlanificacionForm()
    taller = Taller.query.filter_by(id_docente=current_user.id_docente, taller_id=taller_id).first_or_404()

    if form.validate_on_submit():  # Validación del formulario
        nueva_planificacion = Planificacion(
            taller_id=taller_id,
            mes=form.mes.data,
            habilidades=form.habilidades.data,
            recursos=form.recursos.data,
            actividades=form.actividades.data,
            estado=form.estado.data
        )
        db.session.add(nueva_planificacion)
        db.session.commit()
        flash('Planificación creada exitosamente')
        return redirect(url_for('planificacion_docente.listar_planificaciones_docente'))

    return render_template('user/nueva_planificacion.html', taller=taller, form=form)

# Ruta para editar una planificación existente desde la perspectiva del docente
@planificacion_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar_planificacion_docente(id):
    form = PlanificacionForm()
    planificacion = Planificacion.query.filter_by(id_planificacion=id).first_or_404()

    if form.validate_on_submit():  # Validación del formulario
        planificacion.mes = form.mes.data
        planificacion.habilidades = form.habilidades.data
        planificacion.recursos = form.recursos.data
        planificacion.actividades = form.actividades.data
        planificacion.estado = form.estado.data
        db.session.commit()
        flash('Planificación actualizada exitosamente')
        return redirect(url_for('planificacion_docente.listar_planificaciones_docente'))

    # Pre-cargar datos en el formulario
    form.mes.data = planificacion.mes
    form.habilidades.data = planificacion.habilidades
    form.recursos.data = planificacion.recursos
    form.actividades.data = planificacion.actividades
    form.estado.data = planificacion.estado

    return render_template('user/editar_planificacion.html', planificacion=planificacion, form=form)
