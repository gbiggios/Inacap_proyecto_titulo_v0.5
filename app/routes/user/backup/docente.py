from datetime import date
from flask import Blueprint, redirect, render_template, abort, url_for
from flask_login import login_required, current_user
from ....models import Taller

# Blueprint principal para las vistas generales del docente
docente_bp = Blueprint('docente', __name__, url_prefix='/docente')

@docente_bp.route('/')
@login_required
def index():
    # Redirige a la página de dashboard
    return redirect(url_for('docente.dashboard'))


@docente_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_docente and not current_user.is_admin:
        abort(403)

    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    current_date = date.today()
    return render_template('user/docente_dashboard.html', talleres=talleres, current_date=current_date)
