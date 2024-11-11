from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user
from app.models import Taller, EstudianteTaller
from app.routes.admin.decorators import admin_required  # Importar el decorador desde el archivo adecuado

# Crear el Blueprint
admin_bp = Blueprint('admin', __name__)

# Ruta para el dashboard de administrador
@admin_bp.route('/dashboard')
@login_required
@admin_required  # Aplicar el decorador
def dashboard():
    
    return render_template('admin/admin_dashboard.html')
