from flask import Blueprint, render_template
from flask_login import login_required, current_user
from ...models import Taller, Clase

# Definir el Blueprint
docentes_talleres_bp = Blueprint('docente_talleres', __name__)

@docentes_talleres_bp.route('/talleres')
@login_required
def talleres():
    # Obtener los talleres asignados al docente actual
    talleres = Taller.query.filter_by(id_docente=current_user.id_docente).all()
    
    # Si no tiene talleres, muestra un mensaje adecuado
    if not talleres:
        return render_template('user/no_talleres.html')  # Esta es la página donde informas que no hay talleres
    
    return render_template('user/talleres.html', talleres=talleres)

@docentes_talleres_bp.route('/taller/<int:taller_id>')
@login_required
def taller_detalle(taller_id):
    # Obtener el taller y sus clases
    taller = Taller.query.get_or_404(taller_id)
    clases = Clase.query.filter_by(taller_id=taller_id).all()

    return render_template('user/taller_detalle.html', taller=taller, clases=clases)
