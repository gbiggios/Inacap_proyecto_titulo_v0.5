from flask import Flask, redirect, url_for
from flask_caching import Cache
from flask_mail import Mail
from .extensions import db, csrf, login_manager
from app.models import User

# Crear instancias
cache = Cache()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')

    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60 * 60

    # Inicializar extensiones
    cache.init_app(app)
    mail.init_app(app)
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importar y registrar blueprints
    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    from app.routes.user import docente_bp
    app.register_blueprint(docente_bp, url_prefix='/docente')

    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Redirigir la raíz al dashboard del docente
    @app.route('/')
    def index():
        return redirect(url_for('docente.dashboard'))

    return app
