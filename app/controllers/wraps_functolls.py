from functools import wraps
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy import insert
from ..models.hausz_mapa import LogAlteracoesEstoques

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
        print("insere LOG")
       
        '''
        try:
            with db.engine.begin() as conn:
                result = conn.execute(
                    insert(LogAlteracoesEstoques),

                    [
                        {"idusuario": "sandy", "idprodutoalterado": kwargs.get('')},
                        {"idmarcaalterada": kwargs.get('brand'), "tipoalteracao": "Patrick Star",
                        "valoranterior":"","valoralterado":kwargs.get(''),"dataalteracao":kwargs.get('dataatualizacao')}
                    ]
                )
                conn.commit()  
        except:
            pass
        '''

       
        return f(*args, **kwargs)
    return hausz_mapa_update_logs

    
def call_procedure_saldo(f):
    @wraps(f)
    def hausz_mapa_update_saldo(*args, **kwargs):
        print('hausz_mapa_update_saldo',kwargs)
        print("call procedure saldos- INSERINDO SALDOS NOS",kwargs)

        try:
            with db.engine.begin() as conn:
                exec = (text(
                    """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        float(kwargs.get('sd')), str(kwargs.get('ref')), int(kwargs.get('brand')))))
                exec_produtos = conn.execute(exec)
                print("call procedure saldos- INSERINDO SALDOS NOS",kwargs)
        except:
            print('erro')
        return f(*args, **kwargs)
    return hausz_mapa_update_saldo


def call_procedure_prazos(f):
    @wraps(f)
    def hausz_mapa_update_prazo(*args, **kwargs):
        print(kwargs)
   
        print("call procedure prazos - hausz_mapa_update_prazo",kwargs)
        try:
            with db.engine.begin() as conn:
                    exec = (text("""EXEC Estoque.SP_AtualizaPrazoProducao @Sku = '{}' ,@PrazoProducao = {}, @PrazoEstoqueFabrica """.format(
                        str(kwargs.get('ref')),float(kwargs.get('pz')), int(kwargs.get('brand')))))

                    exec_produtos = conn.execute(exec)
                    print("call procedure prazos - hausz_mapa_update_prazo",kwargs)

        except:
            print('erro')
       
    return hausz_mapa_update_prazo


@verify_group_users_hausz_mapa
def get_id_usuario(*args, **kwargs):
    """Rece ID usuario na sessão e verifica o grupo ao qual pertence e as permissoes"""
    print("usuario")


