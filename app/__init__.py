from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask import redirect, url_for, flash
from config import SECRET_KEY, SQLALCHEMY_BINDS, SQLALCHEMY_DATABASE_URI
from flask_bootstrap import Bootstrap

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_BINDS'] = SQLALCHEMY_BINDS
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SQLALCHEMY_POOL_SIZE'] = 370
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
    app.config['MAX_CONTENT_LENGTH'] = 2 * 7024 * 7024
    app.config['UPLOAD_EXTENSIONS'] = ['.pdf', '.xlsx', '.csv', '.png', '.jpg']
    app.config['UPLOAD_PATH'] = 'uploads'

    db.init_app(app)
    Bootstrap(app)
    from .models.hausz_mapa import configure as config_db, Usuarios
    config_db(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is not None:
            return Usuarios.query.get(int(user_id))
        return None

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Faça o login!')
        return redirect(url_for('login.login_usuario'))

    with app.app_context():
        from .admin.admin import adm
        from .admin.login import login
       
        from .admin.index import index
        from .uploadestoque.estoques import uploadestoques

        app.register_blueprint(index)
        app.register_blueprint(adm)
        app.register_blueprint(login)
        app.register_blueprint(uploadestoques)
     

    return app
