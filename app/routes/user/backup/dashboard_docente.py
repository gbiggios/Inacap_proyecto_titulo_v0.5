from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from flask_login import login_required, current_user

from app.forms import AsistenciaEstudianteForm
from ...models import Taller, Clase, AsistenciaEstudiante
from ...extensions import db
from sqlalchemy.orm import sessionmaker

# Definir el Blueprint
docente_bp = Blueprint('docente', __name__)

# Ruta para el Dashboard del docente
@docente_bp.route('/dashboard')
@login_required
def dashboard():
    # Obtener los talleres asignados al docente actual
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    
    return render_template('user/docente_dashboard.html', talleres=talleres)



@docente_bp.route('/cargar_clases/<int:taller_id>')
@login_required
def cargar_clases(taller_id):
    # Consulta para obtener las clases del taller específico
    clases = Clase.query.filter_by(taller_id=taller_id).all()

    # Verifica si se recuperaron clases
    if not clases:
        return jsonify({"error": "No se encontraron clases para este taller"}), 404

    # Estructura los datos para enviar al frontend
    clases_data = [
        {
            'id': clase.id_clase, 
            'nombre': clase.taller.nombre if clase.taller else 'Taller no disponible',  # Verifica si la relación está disponible
            'fecha': clase.fecha.strftime('%d/%m/%Y')
        } for clase in clases
    ]
    
    # Devolver las clases en formato JSON
    return jsonify(clases_data)
