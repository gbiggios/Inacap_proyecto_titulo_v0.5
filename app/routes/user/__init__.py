from .docentes import docente_bp  # Dashboard del docente
from .docentes_talleres import docentes_talleres_bp  # Talleres del docente
from .docente_clases import docente_clases_bp  # Detalles de clase
from .docentes_planificaciones import docente_planificaciones_bp

# Registrar los blueprints
docente_bp.register_blueprint(docentes_talleres_bp, url_prefix='/talleres')
docente_bp.register_blueprint(docente_clases_bp, url_prefix='/clases')
docente_bp.register_blueprint(docente_planificaciones_bp, url_prefix='/planificaciones')  # Aquí registramos el Blueprint de planificaciones