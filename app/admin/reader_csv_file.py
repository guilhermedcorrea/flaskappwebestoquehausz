import csv
from itertools import groupby, chain
import collections
from functools import wraps

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
    def wrapper(*args, **kwargs):

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
    return wrapper


def call_procedure_prazo_hausz_mapa(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
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
    return wrapper


def insert_log_produto(*args, **kwargs):
   
    with db.engine.begin() as conn:

        stmt = (
            insert(LogEstoqueFornecedor).
            values(IdUsuario=1,SKU=kwargs.get('SKU'), IdMarca=kwargs.get('IDMARCA'),IdTipo=12
            ,ValorAnterio=kwargs.get('QUANTIDADE')
            ,ValorAlterado=kwargs['saldo'],PrazoProducaoAnterior=kwargs.get('PRAZOANTERIOR')
            ,PrazoProducaoAlterado=kwargs.get('PRAZOANTERIOR'),DataAlteracao= kwargs.get('DATAATUALIZADO'))
            )
        exec_produtos = conn.execute(stmt)


def select_produtos(*args, **kwargs):
    print('aquiiiiiiii',kwargs)
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
            WHERE pbasico.SKU = '{}'""".format(kwargs['sku'])))

        execquery = conn.execute(query_produto).all()
        for exc in execquery:
          
            print('logs',exc['SKU'],kwargs['saldo'],'anterior ~ >', exc['Quantidade'],exc['PrazoOperacional'])
            data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))


            insert_log_produto(SKU = exc['SKU'],IDPRODUTO = int(exc['IdProduto']),QUANTIDADE = float(exc['Quantidade']),DATAATUALIZADO = data    
            ,PRAZOANTERIOR = int(exc['PrazoOperacional']) ,MARCA = str(exc['Marca']),IDMARCA = exc['IdMarca'], saldo = kwargs['saldo'])
            
            
@call_procedure_saldo_hausz_mapa
def update_saldo_produtos(*args, **kwargs):
    """Recebe parametros de  entrada"""
    print("update saldo", kwargs)
 

    print('update saldo hausz produtos',
          kwargs['sku'], kwargs['saldo'], kwargs['idmarca'])


@call_procedure_prazo_hausz_mapa
def update_prazo_produtos(*args, **kwargs):
    print('procedure prazo', kwargs)

    print("call procedure prazos - hausz_mapa_update_prazo", kwargs)


def get_prazos(*args, **kwargs):
    items = list(chain.from_iterable(args))
    for item in items:

        if len(item.get('PRAZO')) > 0:
            prazo = int(item.get('PRAZO'))

      
            prazolog = float(item.get('PRAZO'))
            update_prazo_produtos(sku=item.get(
                'SKU'),)


def retorna_valores(ref):
    # teste retorno Marca

    with db.engine.begin() as conn:
        exec = (text("""
            SELECT pfornecedor.PrazoProducao,brand.Marca
            ,basico.[IdProduto],basico.[SKU],basico.[IdMarca]  
            ,basico.[SaldoAtual]   
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as basico
            JOIN [HauszMapa].[Produtos].[Marca] as brand
            ON brand.IdMarca = basico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pfornecedor
            ON pfornecedor.SKU = basico.[SKU]
            WHERE basico.[SKU] = '{}' AND basico.[EstoqueAtual] = 3 """.format(ref)))

        exec_produto = conn.execute(exec).all()
        for produto in exec_produto:
            try:
                dict_items = {
                    "sku": produto['SKU'],
                    "idmarca": produto['IdMarca'],
                    "idproduto": produto['IdProduto'],
                    "saldo": produto['SaldoAtual'],
                    "prazo": produto['PrazoProducao']
                }
                yield dict_items
            except:
                print("error")


class ReaderExcel:
    grouped = collections.defaultdict(list)

    def __init__(self, file):
        self.file = file
        self.listas = []
        self.dataatual = str(datetime.today().strftime(
            '%Y-%m-%d %H:%M')).split()[0]

    def reader_csv(self, file):
        with open(file, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter=";", skipinitialspace=True)
            for rows in reader:
                items = {}
                sku_produto = str(rows['SKU'].strip())
                dicts = list(retorna_valores(rows['SKU']))

                if next(filter(lambda x: x['sku'] == sku_produto, dicts), None):
                    lista_produto = dicts[0]

                    dict_produtos = {}
                    try:

                        dict_produtos['SKU'] = lista_produto['sku']
                    except:
                        pass

                    try:
                        saldo_produto = str(rows['SALDO']).replace(
                            ".", "").replace(",", ".")
                        num = float(saldo_produto)
                        dict_produtos['SALDO'] = num

                    except:
                        pass

                    try:
                        dict_produtos['PRAZO'] = rows['PRAZO']

                    except:
                        pass

                    try:
                        dict_produtos['PRAZOANTERIOR'] = lista_produto['prazo']
                    except:
                        pass

                    try:
                        dict_produtos['SALDOANTERIOR'] = lista_produto['prazo']
                    except:
                        pass

                    try:
                        dict_produtos['IDPRODUTO'] = lista_produto['idproduto']
                    except:
                        pass

                    try:
                        dict_produtos['IDMARCA'] = lista_produto['idmarca']
                    except:
                        pass

                    self.listas.append(dict_produtos)


    def group_by(self, key):
        def key(key): return key['SKU']

    def get_produtos(self):
        for item in self.listas:
            self.grouped[item['SKU']].append(item)
        lista_saldos = []
        for key, group in self.grouped.items():

            get_prazos(group)

            lista_saldos = []
            valores = list(chain(group))
            produtos_valores = valores
            if next(filter(lambda x: 'SKU' in x, produtos_valores), None):
                for valores in produtos_valores:

                    lista_saldos.append(valores['SALDO'])

            saldop = float(sum(lista_saldos))
            produtosomado = {}
            try:
                produtosomado['sku'] = valores['SKU']
            except:
                produtosomado['sku'] = 'NotFound'
            try:
                produtosomado['saldo'] = saldop
            except:
                produtosomado['saldo'] = float(0)
            try:
                produtosomado['idmarca'] = valores['IDMARCA']
            except:
                produtosomado['idmarca'] = 'notfound'
            try:
                produtosomado['idproduto'] = valores['IDPRODUTO']
            except:
                produtosomado['idproduto'] = 'notfound'
            try:
                produtosomado['saldoanterior'] = valores['SALDOANTERIOR']
            except:
                produtosomado['saldoanterior'] = float(0)

            try:
                produtosomado['dataatual'] = self.dataatual
            except:
                produtosomado['dataatual'] = 'notfound'



            update_saldo_produtos(saldo=produtosomado['saldo'], sku=produtosomado['sku'], idmarca=produtosomado['idmarca'])
            #         select_produtos(sku=produtosomado['sku'], saldo=produtosomado['saldo'])

            select_produtos(sku=produtosomado['sku'], saldo=produtosomado['saldo'])
