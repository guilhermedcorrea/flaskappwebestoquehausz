import csv
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy



from ..controllers.wraps_functolls import (verify_group_users_hausz_mapa
, create_log_operations,create_log_operations, call_procedure_saldo, call_procedure_prazos)




db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


@verify_group_users_hausz_mapa
def get_id_user(*args, **kwars):
    
    pass

@call_procedure_prazos
def update_prazos_skus(*args, **kwarsg):
    pass

@call_procedure_saldo
def update_saldos_skus(*args, **kwargs):

    try:

        with db.engine.begin() as conn:

            exec = (text(
                    """EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        args[0], args[1], args[2])))
            exec_produtos = conn.execute(exec)


           
    except:
            print('erro')



@create_log_operations
def get_produtos(*args, **kwargs):
    with db.engine.connect() as conn:
        exec = (text("""
            SELECT basico.[IdProduto],basico.[SKU],basico.[NomeProduto] ,basico.[IdMarca]
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as basico
            JOIN [HauszMapa].[Produtos].[Marca] as brand
            ON brand.IdMarca = basico.IdMarca
            WHERE basico.SKU = '{}'""".format(args[0])))
        exec_sku_produto = conn.execute(exec).all()
        for produto in exec_sku_produto:
            try:
                dict_produtos = {
                    'SKU':produto['SKU'],
                    'NomeProduto':produto['NomeProduto'],
                    'IDMARCA':produto['IdMarca']}

                yield dict_produtos
            except:
                print("error teste")
                
            
        

class ReaderCsv:
    def __init__(self, path):
        self.path = path
        self.dict_rows = {}

    def reader_csv(self, file):
  
        with open(file, newline='') as csvfile:

            reader = csv.DictReader(
                csvfile, delimiter=";", skipinitialspace=True)
            for row in reader:
        
                try:

                    if len(row['PRAZO']) == 0 and len(row['SALDO']) !=0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(".","").replace(",",".").strip())
                            saldo = float(saldo)
                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(".","").replace(",",".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        idmarca = str(row['IDMARCA'].strip())
                        idmarca = int(idmarca)

                     
                        dicts = list(get_produtos(sku))
                        print(dicts)
                      
                        #select_hausz_mapa(row['SKU'], row['SALDO'], row['IDMARCA'], row['PRAZO'])

                    elif len(row['SALDO']) == 0 and len(row['PRAZO']) !=0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(".","").replace(",",".").strip())
                            saldo = float(saldo)
                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(".","").replace(",",".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        idmarca = str(row['IDMARCA'].strip())
                        idmarca = int(idmarca)

              
                        dicts = list(get_produtos(sku))
                        print(dicts)

                    elif len(row['PRAZO']) != 0 and len(row['SALDO']) != 0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(".","").replace(",",".").strip())
                            saldo = float(saldo)
                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(".","").replace(",",".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        idmarca = str(row['IDMARCA'].strip())
                        idmarca = int(idmarca)

                        dicts = list(get_produtos(sku))
                        print(dicts)
                        
                      
                        print('opção3', sku, saldo, prazo, idmarca)

                    else:
                        print('erro')
                        print(row['SKU'], row['SALDO'], row['IDMARCA'], row['PRAZO'])
                except:
                    print("error campos nao encontrados")