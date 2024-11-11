from io import BytesIO
from flask import Blueprint, flash, render_template, redirect, send_file, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from flask_mail import Message
import pandas as pd
from app.routes.admin.decorators import admin_required
from ...models import DOCENTE, Clase, EstudianteTaller, Estudiantes, Taller
from ...extensions import db
from app.forms import ClaseForm
from ...extensions import mail

clases_bp = Blueprint('clases_admin', __name__)


from app.forms import ClaseForm

from app.utils import enviar_notificacion_suspension




@clases_bp.route('/', endpoint='clases_admin_home')
@login_required
@admin_required
def clases():
    talleres = Taller.query.all()
    form = ClaseForm()  # Instancia el formulario
    return render_template('admin/clases.html', talleres=talleres, form=form)

@clases_bp.route('/create', methods=['POST'], endpoint='clases_admin_create')
@login_required
@admin_required
def create_clase():
    taller_id = request.form['taller_id']
    fecha = request.form['fecha']
    comentario_bitacora = request.form.get('comentario_bitacora')

    nueva_clase = Clase(
        taller_id=taller_id,
        fecha=fecha,
        comentario_bitacora=comentario_bitacora
    )

    db.session.add(nueva_clase)
    db.session.commit()
    return redirect(url_for('admin.clases_admin.clases_admin_home'))

@clases_bp.route('/multiple', methods=['POST'], endpoint='clases_admin_create_multiple')
@login_required
@admin_required
def create_multiple_clases():
    taller_id = request.form['taller_id']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    dia_semana = request.form['dia_semana']
    comentario_bitacora = request.form.get('comentario_bitacora')

    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
    dias_semana = {'Lunes': 0, 'Martes': 1, 'Miércoles': 2, 'Jueves': 3, 'Viernes': 4}
    dia_semana_num = dias_semana[dia_semana]

    while fecha_inicio <= fecha_fin:
        if fecha_inicio.weekday() == dia_semana_num:
            nueva_clase = Clase(
                taller_id=taller_id,
                fecha=fecha_inicio,
                comentario_bitacora=comentario_bitacora
            )
            db.session.add(nueva_clase)
        fecha_inicio += timedelta(days=1)

    db.session.commit()
    return redirect(url_for('admin.clases_admin.clases_admin_home'))

@clases_bp.route('/clases/<int:taller_id>', methods=['GET'], endpoint='obtener_clases')
@login_required
@admin_required
def obtener_clases(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    clases = taller.clases
    form = ClaseForm()
    return render_template('admin/clases_lista.html', clases=clases, form=form)  # Pasar 'form' al template


@clases_bp.route('/<int:id_clase>/edit', methods=['GET', 'POST'], endpoint='clases_admin_edit')
@login_required
@admin_required
def edit_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    if request.method == 'POST':
        clase.comentario_bitacora = request.form['comentario_bitacora']
        db.session.commit()
        return redirect(url_for('admin.clases_admin.clases_admin_home'))
    return render_template('admin/edit_clase.html', clase=clase)

@clases_bp.route('/exportar_bitacoras/<int:taller_id>', methods=['GET'], endpoint='exportar_bitacoras')
@login_required
@admin_required
def exportar_bitacoras(taller_id):
    taller = Taller.query.get_or_404(taller_id)
    clases = Clase.query.filter_by(taller_id=taller_id).order_by(Clase.fecha).all()

    # Crear datos para exportar a Excel
    data = []
    for clase in clases:
        data.append({
            'Fecha': clase.fecha.strftime('%Y-%m-%d'),
            'Comentario de Bitácora': clase.comentario_bitacora or 'N/A'
        })

    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name=f'Bitacoras_{taller.nombre[:30]}')

    output.seek(0)
    return send_file(
        output,
        download_name=f'bitacoras_{taller.nombre.replace(" ", "_")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


#Suspension
@clases_bp.route('/suspender/<int:id_clase>', methods=['POST'], endpoint='suspender_clase')
@login_required
@admin_required
def suspender_clase(id_clase):
    clase = Clase.query.get_or_404(id_clase)
    taller = Taller.query.get(clase.taller_id)
    estudiantes = Estudiantes.query.join(EstudianteTaller).filter_by(taller_id=taller.taller_id).all()

    # Marcar la clase como suspendida
    clase.suspendida = True
    db.session.commit()

    # Llamar a la función de notificación
    enviar_notificacion_suspension(taller, estudiantes, clase.fecha)

    flash('Clase suspendida y notificaciones enviadas a los estudiantes.', 'info')
    return redirect(url_for('admin.clases_admin.clases_admin_home'))
