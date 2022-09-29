import csv
from itertools import groupby, chain
import collections
from functools import wraps
import re
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from ..models.hausz_mapa import LogAlteracoesEstoques
from datetime import datetime
from ..models.hausz_mapa import LogEstoqueFornecedor

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


def call_procedure_saldo_hausz_mapa(f):
    @wraps(f)
    def update_saldo(*args, **kwargs):
        print('saldoooo Calling decorated function',kwargs.get('sku'), kwargs.get('saldo'))
       
        try:
            print('Calling procedure update SALDO', kwargs)
            with db.engine.begin() as conn:

                exec = (text(
                    """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        kwargs.get('saldo'), kwargs.get('sku'), kwargs.get('idmarca'))))
                exec_produtos = conn.execute(exec)
                print(kwargs.get('sku'), kwargs.get('saldo'))

        except:
            print('erro')
        
 
        return f(*args, **kwargs)
    return update_saldo


@call_procedure_saldo_hausz_mapa
def insert_log_produtos_saldos(*args, **kwargs):
    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    """Recebe parametros de entrada e cadastra log saldo"""
    print('log saldo',kwargs,kwargs.get('sku'), kwargs.get('saldo'))
    with db.engine.begin() as conn:
        
        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('sku'), IdMarca=kwargs.get('IdMarca'),IdTipo=12,
            PrazoProducaoAlterado=kwargs.get('prazo'),ValorAnterio = kwargs.get('saldoanterior')
            ,PrazoProducaoAnterior=kwargs.get('prazoanterior'),DataAlteracao= data)
            )
        exec_produtos = conn.execute(stmt)


def call_procedure_prazo_hausz_mapa(f):
    @wraps(f)
    def update_prazo(*args, **kwargs):
        
        print('prazo Calling decorated function', kwargs.get('sku'), kwargs.get('prazo'))

        print('Calling procedure update PRAZO', kwargs)
        try:
            with db.engine.begin() as conn:

                exec = (text("""EXEC Estoque.SP_AtualizaPrazoProducao @Sku = '{}' ,@PrazoProducao = {}, @PrazoEstoqueFabrica """.format(
                    str(kwargs.get('sku')), float(kwargs.get('prazo')), int(kwargs.get('idmarca')))))

                exec_produtos = conn.execute(exec)
                print("call procedure prazos - hausz_mapa_update_prazo", kwargs)
        except:
            print("erro prazo")
            return f(*args, **kwargs)
 
    return update_prazo

@call_procedure_prazo_hausz_mapa
def insert_log_produtos_prazos(*args, **kwargs):
    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    """Recebe parametros de entrada e cadastra log prazo"""
    print('log prazoproduto',kwargs.get('sku'), kwargs.get('prazo'))

    with db.engine.begin() as conn:

        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('sku'), IdMarca=kwargs.get('IdMarca'),IdTipo=12,
            PrazoProducaoAlterado=kwargs.get('prazo'),ValorAnterio=kwargs.get('saldo')
            ,PrazoProducaoAnterior=kwargs.get('prazoanterior'),DataAlteracao= data)
            )
        exec_produtos = conn.execute(stmt)
    

def key_func(k):
	return k['SKU']


def select_produtos_hausz_mapa(*args, **kwargs):
    with db.engine.begin() as conn:
        query_produto = (text("""
            SELECT TOP(1) psaldo.Quantidade,pbasico.IdProduto
            ,CONVERT(VARCHAR, psaldo.DataAtualizado, 23) as datas
            ,pprazof.PrazoOperacional,pmarca.Marca,pbasico.[IdProduto]
            ,pbasico.[SKU],pbasico.[NomeProduto]
            ,pbasico.[EstoqueAtual],pbasico.[SaldoAtual] ,pbasico.[IdMarca]
            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] AS pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN  [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pprazof
            ON pprazof.SKU = pbasico.SKU
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            WHERE pbasico.SKU = '{}'""".format(kwargs['SKU'])))

        execquery = conn.execute(query_produto).all()
        try:
            for produtos in execquery:
                produtos_dict = {
                    'SKU':produtos['SKU'],
                    'SALDOANTERIOR':produtos['Quantidade'],
                    'PRAZOANTERIOR':produtos['PrazoOperacional'],
                    'IDMARCA':produtos['IdMarca'],
                    'IDPRODUTO':produtos['IdProduto']}

            yield produtos_dict
        except:
            print("erro query")


def reader_csv(file):
    print("arquivooo", file)
   
    with open(file, newline='', encoding='latin-1') as csvfile:
        try:
            reader = csv.DictReader(
                csvfile, delimiter=";", skipinitialspace=True)

            rows = [row for row in reader]
        except:
            print("erro file")
        
        produtos = sorted(rows, key=key_func)
        for key, value in groupby(produtos, key_func):
            lista_saldos = []
            saldos = list(filter(lambda item: item['SALDO'],value))
            for saldo in saldos:
                values = list(select_produtos_hausz_mapa(SKU = str(saldo.get('SKU')).strip()))
                values = values[0]
                #print('RETORNO CONSULTA',values['SKU'], values['SALDOANTERIOR'], values['PRAZOANTERIOR'], values['IDMARCA'], values['IDPRODUTO'])
                lista_saldos.append(float(str(saldo.get('SALDO').replace(".","").replace(",",".").strip())))
                print(values)

            produtos_dicts = {}
            try:
                produtos_dicts['SKU'] = str(saldo.get('SKU')).strip()
            except:
                produtos_dicts['SKU'] = 'SKU NAO ENCONTRADO'
                print('erro sku', saldo['SKU'])

            try:
                produtos_dicts['PRAZO'] = int(saldo.get('PRAZO'))
            except:
                produtos_dicts['PRAZO'] = int(0)
                print("erro prazo", saldo['SKU'], 'prazo invalido')
            try:
                produtos_dicts['SALDO'] = sum(lista_saldos)
            except:
                produtos_dicts['SALDO'] = 'SALDO NAO ENCONTRADO'
                print('erro saldo', saldo['SKU'],'SALDO INVALIDO')
            try:
                produtos_dicts['SALDOANTERIOR'] = float(values['SALDOANTERIOR'])
            except:
                print("erro saldo anterior")
            try:
                produtos_dicts['PRAZOANTERIOR'] = int(values['PRAZOANTERIOR'])
            except:
                print("erro prazoanterior")

            try:
                produtos_dicts['IDMARCA'] = values['IDMARCA']
            except:
                print("erro idmarca")

            try:
                produtos_dicts['IDPRODUTO'] = values['IDPRODUTO']
            except:
                print("erro id produto")
         
            if re.search('\d+',str(produtos_dicts['PRAZO'])):
                
                try:
                    insert_log_produtos_prazos(sku= produtos_dicts['SKU'], prazo = produtos_dicts['PRAZO']
                        , prazoanterior = produtos_dicts['PRAZOANTERIOR']
                            ,idmarca = produtos_dicts['IDMARCA'], idproduto = produtos_dicts['IDPRODUTO'])
                except:
                    print("erro log prazo")
            try:
                insert_log_produtos_saldos(sku= produtos_dicts['SKU'],
                     saldo=produtos_dicts['SALDO'], saldoanterior = produtos_dicts['SALDOANTERIOR']
                        , idmarca = produtos_dicts['IDMARCA'], idproduto = produtos_dicts['IDPRODUTO'])
            except:
                print("erro log saldo")
         
         
           
