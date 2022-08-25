import csv
from itertools import groupby, chain
import collections
from functools import wraps

from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import insert
from ..models.hausz_mapa import LogAlteracoesEstoques

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
                            str(kwargs.get('sku')),float(kwargs.get('prazo')), int(kwargs.get('idmarca')))))

                        exec_produtos = conn.execute(exec)
                        print("call procedure prazos - hausz_mapa_update_prazo",kwargs)
        except:
            print("erro prazo")
            return f(*args, **kwargs)
    return wrapper


def create_log_udapte_products(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        print(kwargs)
        '''
        try:
            with db.engine.begin() as conn:
                result = conn.execute(
                    insert(LogAlteracoesEstoques),
                    [
                        {"idusuario": 1, "idprodutoalterado": kwargs.get('idproduto')},
                        {"idmarcaalterada": kwargs.get('idmarca'), "tipoalteracao": 1,
                        "valoranterior":kwargs.get('saldoanterior'),"valoralterado":kwargs.get('saldo'),"dataalteracao":"2022-08-25", }
                    ]
                )
                conn.commit()  
        except:
            pass
        '''

       
        return f(*args, **kwargs)
    return wrapper

@create_log_udapte_products
def get_updates_produtos(*args, **kwargs):

    print('testeeeeeeeeee',kwargs)
    try:
        with db.engine.begin() as conn:
            result = conn.execute(
                insert(LogAlteracoesEstoques),
                [
                    {"idusuario": 1, "idprodutoalterado": kwargs.get('idproduto')},
                    {"idmarcaalterada": kwargs.get('idmarca'), "tipoalteracao": 1,
                        "valoranterior":kwargs.get('saldoanterior'),"valoralterado":kwargs.get('saldo'),"dataalteracao":"2022-08-25", }
                ]
            )
            conn.commit()  

    except:
            pass
       
    print('criando log produtos',kwargs)
   

  
@call_procedure_saldo_hausz_mapa
def update_saldo_produtos(*args, **kwargs):
    """Recebe parametros de  entrada"""
    print("update saldo", kwargs)
    get_updates_produtos(kwargs['saldo']
        , kwargs.get('idmarca'), kwargs.get('idproduto'), kwargs.get('idmarca'), kwargs.get('saldoanterior'))


    
    print('update saldo hausz produtos',kwargs['sku'], kwargs['saldo'], kwargs['idmarca'])
 

@call_procedure_prazo_hausz_mapa
def update_prazo_produtos(*args, **kwargs):
    print('procedure prazo', kwargs)

    print("call procedure prazos - hausz_mapa_update_prazo",kwargs)


def get_prazos(*args, **kwargs):
    items = list(chain.from_iterable(args))
    for item in items:

        if len(item.get('PRAZO')) > 0:
            prazo = int(item.get('PRAZO'))

            get_updates_produtos(sku = item.get('SKU'), prazo = prazo
            , idmarca = item.get('IDMARCA'), idproduto = item.get('IDPRODUTO'), prazoanterior = item.get('PRAZOANTERIOR'))
            prazolog = float(item.get('PRAZO'))
            update_prazo_produtos(sku = item.get('SKU'), prazo = prazolog, idmarca = item.get('IDMARCA'))

def retorna_valores(ref):
    #teste retorno Marca
 
   
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
                dict_items={
                    "sku":produto['SKU'],
                    "idmarca":produto['IdMarca'],
                    "idproduto":produto['IdProduto'],
                    "saldo":produto['SaldoAtual'],
                    "prazo":produto['PrazoProducao']
                }
                yield dict_items
            except:
                print("error")

class ReaderExcel:
    grouped = collections.defaultdict(list)
    
    def __init__(self,file):
        self.file = file
        self.listas = []

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
                        saldo_produto =  str(rows['SALDO']).replace(".","").replace(",",".")
                        num = float(saldo_produto)
                        dict_produtos['SALDO'] =  num

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
        key = lambda key: key['SKU']


    def get_produtos(self):
        for item in self.listas:
            self.grouped[item['SKU']].append(item)

        for key, group in self.grouped.items():
            get_prazos(group)
   
            lista_saldos = []
            valores = list(chain(group))
            produtos_valores = valores[0]
            if next(filter(lambda x: 'SKU' in produtos_valores, produtos_valores), None):
                lista_saldos.append(produtos_valores['SALDO'])

            saldo_produto = sum(lista_saldos)

            update_saldo_produtos(sku=produtos_valores['SKU'], saldo = float(saldo_produto)
                ,idmarca =produtos_valores['IDMARCA'], idproduto = produtos_valores['IDPRODUTO'], saldoanterior = produtos_valores['SALDOANTERIOR'])

