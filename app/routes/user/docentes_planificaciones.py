from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from app.models import Planificacion, Taller
from app.forms import PlanificacionForm
from app.extensions import db

# Crear el Blueprint para las rutas de Planificación para el Docente
docente_planificaciones_bp = Blueprint('docente_planificaciones', __name__, url_prefix='/docente/planificaciones')

# Ruta para listar las planificaciones del docente (solo los talleres asignados al docente)
@docente_planificaciones_bp.route('/', methods=['GET'])
@login_required
def listar_planificaciones_docente():
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()

    if not talleres:
        flash('No tienes talleres asignados para mostrar planificaciones.')
        return redirect(url_for('docente.dashboard'))  # Redirigir al Dashboard si no hay talleres

    taller_seleccionado = talleres[0]  # Seleccionar el primer taller como predeterminado

    # Obtener las planificaciones del taller seleccionado
    planificaciones = Planificacion.query.filter_by(taller_id=taller_seleccionado.taller_id).all()

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

    return render_template(
        'user/gestionar_planificaciones_docente.html',
        talleres=talleres,
        taller_seleccionado=taller_seleccionado,
        planificaciones_por_mes=planificaciones_por_mes,
        siguiente_mes=siguiente_mes,
        puede_crear=puede_crear,
        form=PlanificacionForm()  # Asegúrate de pasar el formulario aquí
    )

# Ruta para ver las planificaciones de un taller específico
@docente_planificaciones_bp.route('/taller/<int:taller_id>', methods=['GET', 'POST'])
@login_required
def ver_planificaciones_taller(taller_id):
    taller = Taller.query.get_or_404(taller_id)

    # Verificar que el docente sea el responsable del taller
    if taller.id_docente != current_user.id_docente:
        flash('No tienes acceso a las planificaciones de este taller.')
        return redirect(url_for('docente_planificaciones.listar_planificaciones_docente'))

    # Obtener las planificaciones del taller seleccionado
    planificaciones = Planificacion.query.filter_by(taller_id=taller_id).all()

    # Listado de meses
    meses = ["marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

    # Diccionario para almacenar las planificaciones por mes
    planificaciones_por_mes = {mes: None for mes in meses}

    # Llenar el diccionario con las planificaciones existentes
    for plan in planificaciones:
        planificaciones_por_mes[plan.mes] = plan

    # Instanciar el formulario
    form = PlanificacionForm()

    # Si el método es POST, se procesan los datos del formulario
    if form.validate_on_submit():
        # Crear o actualizar planificación
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
        return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))

    # Pasamos 'planificaciones_por_mes' al contexto
    return render_template(
        'user/gestionar_planificaciones_docente.html',
        taller_seleccionado=taller,  # Asegúrate de pasar el taller
        planificaciones_por_mes=planificaciones_por_mes,  # Pasamos el diccionario al contexto
        form=form
    )

# Ruta para crear una nueva planificación para un taller
@docente_planificaciones_bp.route('/crear_planificacion', methods=['POST'], endpoint='crear_planificacion')
@login_required
def crear_planificacion():
    taller_id = request.form['taller_id']
    form = PlanificacionForm()

    taller = Taller.query.get_or_404(taller_id)
    if taller.id_docente != current_user.id_docente:
        flash('No tienes acceso para crear una planificación para este taller.')
        return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))

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

    return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=taller_id))

# Ruta para actualizar el objetivo general
@docente_planificaciones_bp.route('/actualizar_objetivo_general', methods=['POST'], endpoint='actualizar_objetivo_general')
@login_required
def actualizar_objetivo_general():
    taller_id = request.form['taller_id']
    taller = Taller.query.get_or_404(taller_id)

    objetivo_general = request.form['objetivo_general']
    taller.objetivo_general = objetivo_general

    db.session.commit()
    flash('Objetivo general actualizado exitosamente.')

    return redirect(url_for('docente_planificaciones.listar_planificaciones_docente'))

# Ruta para editar planificación
@docente_planificaciones_bp.route('/editar_planificacion/<int:id_planificacion>', methods=['POST'])
@login_required
def editar_planificacion(id_planificacion):
    planificacion = Planificacion.query.get_or_404(id_planificacion)  # Obtener la planificación por su ID
    # Procesar la actualización de los datos
    planificacion.habilidades = request.form['habilidades']
    planificacion.recursos = request.form['recursos']
    planificacion.actividades = request.form['actividades']
    planificacion.estado = request.form['estado']
    db.session.commit()  # Guardar los cambios en la base de datos
    flash('Planificación actualizada exitosamente.')
    return redirect(url_for('docente_planificaciones.ver_planificaciones_taller', taller_id=planificacion.taller_id))
