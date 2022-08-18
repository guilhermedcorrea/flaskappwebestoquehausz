import pandas as pd
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import csv
import os
from flask import current_app
from config import UPLOADFOLDER

db = SQLAlchemy()

def configure(app):
    db.init_app(app)
    app.db = db


class AtualizaSaldos:
    def __init__(self, path):
        self.path = path
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self._lista_dicts = []
        self.save_itens = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','admin','files','adminuploads')

    def select_hausz_mapa(self, skuproduto, saldoproduto):
        listas = []
        with db.engine.connect() as conn:
            querychartindex = (text("""
                SELECT  pmarca.Marca,pmarca.IdMarca,pbasico.[IdProduto]
                ,pbasico.[SKU],pbasico.[NomeProduto]
                FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
                JOIN [HauszMapa].[Produtos].[Marca] as pmarca
                ON pmarca.IdMarca = pbasico.IdMarca
                WHERE pbasico.[SKU] in ('{}')""".format(skuproduto)))
            excquerychartindex = conn.execute(querychartindex).all()
            try:
                for dicts in excquerychartindex:
                    dicts_items = {
                        'MARCA': str(dicts['Marca']),
                        'IDMARCA': int(dicts['IdMarca']),
                        'SKU': str(dicts['SKU']),
                        'SALDO': float(saldoproduto),
                        'DATA': self.dataatual

                    }
                    self._lista_dicts.append(dicts_items)
            except:
                print("erro retorno dicionario")


    def reader_excel_file(self):
        try:
            data = pd.read_excel(self.path)
            for i, row in data.iterrows():
                self.select_hausz_mapa(row[0], row[2])

            return self._lista_dicts
        except:
            print("erro retornar dict Saldos")


    def dict_writer(self):
        try:
            filename = 'SaldosGerais' + '_' + self.dataatual .split()[0] + '.csv'
            with open(self.save_itens +filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.lista_produtos[1])
                writer.writeheader()
                for row in self.lista_produtos:
                    writer.writerow(row)
        except:
            print("erro csv log SaldosGerais")


    @staticmethod
    def delete_upload_files():
        try:
            files = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
         
            for file in files:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(os.path.join(UPLOADFOLDER,'app','uploads'), file)
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deleta arquivos SaldosGerais")

    @staticmethod
    def delete_image_files():
        try:
            images = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
            path2 = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
            for file in images:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(path2, file)
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deletar files SaldosGerais")

