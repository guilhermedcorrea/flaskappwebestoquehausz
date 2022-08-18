from flask import Blueprint, render_template, flash, redirect, url_for, request
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import login_user, current_user, logout_user
from werkzeug.security import check_password_hash

login = Blueprint('login', __name__)

from app.models.hausz_mapa import Usuarios, LoginForm

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


def update_status_usuario(bit_logado, status):
    valor = db.engine.execute("""
        UPDATE [HauszMapaDev2].[dbo].[Users]
        SET [bitlogado] ={},
        status_login = '{}',
        [datalogado] = GETDATE()
        WHERE id_usuario = 1""".format(bit_logado, status))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if Usuarios.id_usuario is None:
            return redirect(url_for('login.login_usuario', next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@login.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        update_status_usuario(0, 'Deslogado')
        return redirect(url_for('login.login_usuario'))
    else:
        return redirect(url_for('login.login_usuario'))


@login.route("/login", methods=['GET', 'POST'])
def login_usuario():
    if current_user.is_authenticated:
        return redirect(url_for('admin.index'))

    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = Usuarios.query.filter_by(nome=form.Usuario.data).first()
            print(user)
            if user and check_password_hash(user.password_hash, form.Senha.data):
                update_status_usuario(1, 'Logado')
                login_user(user, remember=form.remember.data)

                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index.dashboard'))
            else:
                flash('Logado com Sucesso')

    return render_template('login.html', title='Login', form=form)


