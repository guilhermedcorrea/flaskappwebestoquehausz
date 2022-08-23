import csv
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from ..controllers.wraps_functolls import (
    verify_group_users_hausz_mapa, create_log_operations, create_log_operations
    , call_procedure_saldo, call_procedure_prazos)


db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


def get_id_marca(ref):
    with db.engine.begin() as conn:
        exec = (text("""SELECT  IdMarca
            FROM [HauszMapa].[Produtos].[ProdutoBasico]
            WHERE SKU='{}'""".format(ref)))
        try:
            exec_produtos = conn.execute(exec).first()
            idmarca = str(exec_produtos[0])
     
            yield idmarca
        except:
            print("notofund")
     
   
@verify_group_users_hausz_mapa
def get_id_user(*args, **kwargs):

    pass

@create_log_operations
@call_procedure_prazos
def update_prazos_skus(*args, **kwargs):
    print(type(kwargs))
    print("INSERINDO PRAZO", kwargs.get('ref'), kwargs('pz')
    , kwargs.get('brand'), kwargs.get('dataatualizacao'))


@create_log_operations
@call_procedure_saldo
def update_saldos_skus(*args, **kwargs):
    print(type(kwargs))
    print("INSERINDO SALDOS", kwargs.get('ref'), kwargs.get('sd')
        ,kwargs.get('brand'), kwargs.get('dataatualizacao'))
 

def get_produtos(*args, **kwargs):
    if isinstance(kwargs, dict):
        idmarca = list(get_id_marca(kwargs.get('ref')))
        print("criando logs", kwargs)
        print(kwargs.get('ref'), kwargs.get('sd'), idmarca = idmarca)

    if isinstance(args, list):
        print("criando logs")
      
        print(kwargs.get('ref'), kwargs.get('sd'), idmarca = idmarca)

class ReaderCsv:
    def __init__(self, path):
        self.path = path
        self.dict_rows = {}
        self.data = str(datetime.today().strftime('%Y-%m-%d %H:%M')).split()[0]
    def reader_csv(self, file):
        with open(file, newline='', encoding='latin-1') as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter=";", skipinitialspace=True)
            for row in reader:
                try:
                    row['IDMARCA'] = list(get_id_marca(row['SKU']))[0]
                    print('branddd',row['IDMARCA'])
                except Exception as e:
                    print(e,'erroidmarca')

                try:

                    if len(row['PRAZO']) == 0 and len(row['SALDO']) != 0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(
                                ".", "").replace(",", ".").strip())
                            saldo = float(saldo)

                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(
                                ".", "").replace(",", ".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        
                        try:
                            idmarca = int(row['IDMARCA'])
                       
                        except:
                            pass
                        try:
                            dataatual = self.data
                        except:
                            pass
                
                     
                        list(update_saldos_skus(ref=sku, sd=saldo, brand=idmarca, dataatualizacao = dataatual))
                    
                    elif len(row['SALDO']) == 0 and len(row['PRAZO']) != 0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(
                                ".", "").replace(",", ".").strip())
                            saldo = float(saldo)
                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(
                                ".", "").replace(",", ".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        try:
                            idmarca = int(row['IDMARCA'])
                           
                        except:
                            pass

                        try:
                            dataatual = self.data
                        except:
                            pass


                        list(update_prazos_skus(ref=sku, vl=prazo, brand=idmarca, dataatualizacao = dataatual))
                        

                    elif len(row['PRAZO']) != 0 and len(row['SALDO']) != 0:
                        sku = str(row['SKU'].strip())
                        try:
                            saldo = str(row['SALDO'].replace(
                                ".", "").replace(",", ".").strip())
                            saldo = float(saldo)
                        except:
                            pass
                        try:
                            prazo = str(row['PRAZO'].replace(
                                ".", "").replace(",", ".").strip())
                            prazo = float(prazo)
                        except:
                            pass
                        try:
                            idmarca = int(row['IDMARCA'])
                        except:
                            pass

                        try:
                            dataatual = self.data
                        except:
                            pass
                       
                        list(update_prazos_skus(ref=sku, pz=prazo, brand=row['IDMARCA'], dataatualizacao = dataatual))
                    else:
                        print('erro')
                        idmarca = int(row['IDMARCA'])
                        list(update_prazos_skus(ref=sku, pz=prazo, brand=idmarca))
                        list(call_procedure_saldo(
                            ref=sku, sd=saldo, brand=idmarca))
                        print('opcao 4')
                except:
                    print(row['SKU'], row['SALDO'], row['PRAZO'])
                  
