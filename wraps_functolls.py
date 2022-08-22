from functools import wraps
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
def configure(app):
    db.init_app(app)
    app.db = db


def verify_group_users_hausz_mapa(f):
    @wraps(f)
    def conditions_acess_users(*args, **kwargs):
        print('Calling decorated function',args, 'acesso usuario')
        return f(*args, **kwargs)
    return conditions_acess_users

def create_log_operations(f):
    @wraps(f)
    def hausz_mapa_update_logs(*args, **kwargs):
        print('Calling decorated function',args, 'update log hausz')
        return f(*args, **kwargs)
    return hausz_mapa_update_logs

def call_procedure_saldo(f):
    @wraps(f)
    def hausz_mapa_update_saldo(*args, **kwargs):
        print('Calling decorated function', args,'call procedore saldos')
        return f(*args, **kwargs)
    return hausz_mapa_update_saldo


def call_procedure_prazos(f):
    @wraps(f)
    def hausz_mapa_update_prazo(*args, **kwargs):
        print('Calling decorated function', args,'call procedore prazoss')
        return f(*args, **kwargs)
    return hausz_mapa_update_prazo


@verify_group_users_hausz_mapa
def get_id_usuario(*args, **kwargs):
    """Rece ID usuario na sessão e verifica o grupo ao qual pertence e as permissoes"""
    print("usuario")


