from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.models import Clase
from app.extensions import db

# Crear el Blueprint
docente_bitacora_bp = Blueprint('docente_bitacora', __name__)

# Ruta para actualizar la bitácora de una clase
@docente_bitacora_bp.route('/<int:clase_id>', methods=['GET', 'POST'])
@login_required
def bitacora_detalle(clase_id):
    clase = Clase.query.get_or_404(clase_id)

    if request.method == 'POST':
        # Actualizar el comentario de la bitácora
        comentario = request.form.get('comentario_bitacora', '')
        if comentario:
            clase.comentario_bitacora = comentario
            db.session.commit()
            flash('Bitácora actualizada correctamente.', 'success')
            return redirect(url_for('docente_bitacora.bitacora_detalle', clase_id=clase.id_clase))

    return render_template('user/bitacora_detalle.html', clase=clase)
