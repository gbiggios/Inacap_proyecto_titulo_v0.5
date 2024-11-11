from flask import Blueprint, render_template, request, redirect, flash, jsonify, url_for
from flask_login import login_required, current_user
from app.models import Planificacion, Taller
from app.forms import PlanificacionForm
from app.extensions import db

# Crear el Blueprint para las rutas de Planificación para el Docente
docente_planificaciones_bp = Blueprint('docente_planificaciones', __name__)

# Ruta para listar las planificaciones del docente (solo los talleres asignados al docente)
@docente_planificaciones_bp.route('/', methods=['GET'])
@login_required
def listar_planificaciones_docente():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()

    if not talleres:
        flash('No tienes talleres asignados para mostrar planificaciones.')
        return redirect(url_for('docente.dashboard'))

    # Seleccionar el primer taller como predeterminado
    taller_seleccionado = talleres[0]

    # Obtener las planificaciones del taller seleccionado
    planificaciones = Planificacion.query.filter_by(taller_id=taller_seleccionado.id).all()

    # Listado de meses
    meses = ["marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    # Diccionario para almacenar las planificaciones por mes
    planificaciones_por_mes = {mes: None for mes in meses}

    # Llenar el diccionario con las planificaciones existentes
    for plan in planificaciones:
        planificaciones_por_mes[plan.mes] = plan

    # Determinar si se puede crear una nueva planificación
    siguiente_mes = None
    puede_crear = True
    for i, mes in enumerate(meses):
        if planificaciones_por_mes[mes] is None:
            siguiente_mes = mes
            if i > 0 and planificaciones_por_mes[meses[i - 1]] is None:
                puede_crear = False
            break

    # Devolver la vista con el contenido dinámico
    return render_template(
        'user/gestionar_planificaciones_docente.html',
        talleres=talleres,
        taller_seleccionado=taller_seleccionado,
        planificaciones_por_mes=planificaciones_por_mes,
        siguiente_mes=siguiente_mes,
        puede_crear=puede_crear,
        form=PlanificacionForm()
    )

# Ruta para cargar las planificaciones de un taller específico sin cambiar la URL
@docente_planificaciones_bp.route('/taller/<int:taller_id>', methods=['GET'])
@login_required
def ver_planificaciones_taller(taller_id):
    taller_seleccionado = Taller.query.get_or_404(taller_id)

    # Obtener las planificaciones del taller seleccionado
    planificaciones = Planificacion.query.filter_by(taller_id=taller_seleccionado.id).all()

    # Listado de meses
    meses = ["marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    # Diccionario para almacenar las planificaciones por mes
    planificaciones_por_mes = {mes: None for mes in meses}

    # Llenar el diccionario con las planificaciones existentes
    for plan in planificaciones:
        planificaciones_por_mes[plan.mes] = plan

    # Renderizar el template para las planificaciones y devolverlo como JSON
    return jsonify({
        'taller_seleccionado': taller_seleccionado.nombre,
        'planificaciones': render_template('user/planificaciones_taller.html', 
                                          planificaciones_por_mes=planificaciones_por_mes, 
                                          taller_seleccionado=taller_seleccionado)
    })


# Ruta para crear una nueva planificación para un taller
@docente_planificaciones_bp.route('/crear_planificacion', methods=['POST'])
@login_required
def crear_planificacion():
    form = PlanificacionForm()
    if form.validate_on_submit():
        taller_id = request.form['taller_id']
        taller = Taller.query.get_or_404(taller_id)

        if taller.id_docente != current_user.id_docente:
            flash('No tienes acceso para crear una planificación para este taller.')
            return redirect(url_for('docente_planificaciones.listar_planificaciones_docente'))

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
        flash('Planificación creada exitosamente.')

        return redirect(url_for('docente_planificaciones.listar_planificaciones_docente'))
