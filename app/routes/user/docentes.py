# app/routes/user/docentes.py
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ...models import Taller

# Definir el Blueprint
docente_bp = Blueprint('docente', __name__)

@docente_bp.route('/dashboard')
@login_required
def dashboard():
    # Obtener los talleres asignados al docente actual
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    
    return render_template('user/docente_dashboard.html', talleres=talleres)
