
import csv
from datetime import datetime
import os
from config import UPLOADFOLDER
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


db = SQLAlchemy()

def configure(app):
    db.init_app(app)
    app.db = db

print(os.path.abspath(os.path.dirname(__file__)) )

class ReaderExcelFile:
    def __init__(self, path):
        self.path = path
        self.file = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','uploadestoque','excel_estoque')
        self.list_dict_saldo = []
        self.list_dict_prazo = []
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
     
        self._lista_dicts = []
        self.save_itens = os.path.join(UPLOADFOLDER, 'app','uploads','excel_estoque')


    def reader_file(self):
      
        filename = os.path.join(self.file,self.path[-1])
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(
                csvfile, delimiter=";", skipinitialspace=True)
            for row in reader:
                print(row)
                dict_saldos = {}
                dict_prazos = {}

                row["SKU"], row['IDMARCA'], row['SALDO'], row['PRAZO']
                try:
                    dict_saldos['SKU'] = str(row["SKU"])
                except:
                    dict_saldos['SKU'] = 'notfound'
                try:
                    dict_saldos['IDMARCA'] = int(row['IDMARCA'])
                except:
                    dict_saldos['IDMARCA'] = 'notfound'
                try:
                    dict_saldos['SALDO'] = float(str(row['SALDO'].replace(".","").replace(",",".")))
                except:
                    dict_saldos['SALDO'] = float(0)
                try:
                    dict_prazos['SKU'] = str(row["SKU"])
                except:
                    dict_prazos['SKU'] = 'notfound'
                try:
                    dict_prazos['IDMARCA'] = int(row['IDMARCA'])
                except:
                    dict_prazos['IDMARCA'] = 'notfound'
                
                try:
                    dict_prazos['PRAZO'] = int(row['PRAZO'])
                except:
                    dict_prazos['PRAZO'] = int(0)

                self.list_dict_saldo.append(dict_saldos)
                self.list_dict_prazo.append(dict_prazos)


            
    def call_hausz_mapa_atualizaproducao(self,sku, prazoproducao, prazofabrica=0):
        lista_dicts = []
        with db.engine.connect() as conn:

            try:

                exec = (text("""EXEC [Estoque].[SP_AtualizaPrazoProducao] @Sku = '{}', @PrazoProducao = {}, @PrazoEstoqueFabrica = {}""".format(sku
                        ,prazoproducao,prazofabrica)))
                exec_produtos = conn.execute(exec)
                dict_itens={
                    "SKU":sku,
                    'PRAZOPRODUCAO':prazoproducao,
                    
                }
                self._lista_dicts.append(dict_itens)

            except:

                print("error")
            

        

    def call_procedure_atualiza_estoque_fornecedor(self, saldo, sku, idmarca):
        lista_dicts = []
        with db.engine.connect() as conn:

            try:
                exec = (text("""EXEC Estoque.SP_AtualizaEstoqueFornecedor @Quantidade = {}, @CodigoProduto = '{}', @IdMarca = {}""".format(
                        saldo, sku, idmarca)))
                exec_produtos = conn.execute(exec)
                dict_itens = {
                    'SKU':sku,
                    'IDMARCA':idmarca,
                    'SALDO':saldo
                }
                self._lista_dicts.append(dict_itens)

            except:
                print("error")
       
                
                    
    def call_procedure_prazo_hausz_mapa(self):
        for prazo in self.list_dict_prazo:
         
            sku = prazo['SKU']
            praz = prazo['PRAZO']
            prazofabrica = 0
            
            dicts = self.call_hausz_mapa_atualizaproducao(sku, praz,0)
           


    def call_procedure_saldo_hausz_mapa(self):
        for saldo in self.list_dict_saldo:
            print(type(saldo['SALDO']))
            sku = str(saldo['SKU'])
            saldoproduto = float(saldo['SALDO']) 
            idmarca = int(saldo['IDMARCA'])

            print(sku, saldoproduto,idmarca)
            dicts = self.call_procedure_atualiza_estoque_fornecedor(saldoproduto,sku,idmarca)
            return dicts
    

    def retorna_valores(self):
        return self._lista_dicts