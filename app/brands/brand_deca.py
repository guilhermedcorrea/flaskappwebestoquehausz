import pandas as pd
import re
from datetime import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask import current_app
from config import UPLOADFOLDER

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


def filtrar_estoques(valores):
    if isinstance(valores, float):
        if valores > 0:
            return valores
        else:
            return 0

    else:
        return 0


def converte_float(valores):
    lista_ajustados = []
    for valor in valores:

        try:
            nums = str(valor.replace(",", "."))
            nums = float(nums)
            lista_ajustados.append(nums)
            return nums
        except:
            lista_ajustados.append(0)
    return lista_ajustados


PDF_FILE = UPLOAD_FOLDER = current_app.config['UPLOAD_PATH']
download_file = os.path.join(UPLOADFOLDER, 'appconversorarquivos', 'app', 'adm', 'uploads')


# recebe arquivo do diretorio da marca deca.

class Deca:
    def __init__(self, path):
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.lista_sheets = []
        self.lista_colunas_filtradas = []
        self.path = path
        self.log = download_file

    # Recebe arquivo pelo parametro path e faz a leitura das abas
    def reader_excel_file(self):

        print('caminho deca file', self.path)
        data = pd.ExcelFile(self.path)
        for sheet in data.sheet_names:

            cont = len(data.parse(sheet))
            if cont > 1000:
                # lista_sheets.append(sheet)
                deca_df = pd.read_excel(self.path, sheet_name=sheet)
                deca_df.fillna(0, inplace=True)

                self.lista_sheets.append(deca_df)

    def unifica_dataframes(self):
        dataframe_deca = pd.concat(self.lista_sheets)
        lista_coluns = dataframe_deca.columns

        for lista in lista_coluns:
            if re.search('Nº do ma.?|do material.?|Nº do material', lista, re.IGNORECASE):
                dataframe_deca[lista]
                self.lista_colunas_filtradas.append(dataframe_deca)

            if re.search('EST DISP.?|EST.?|DISP.?', lista, re.IGNORECASE):
                dataframe_deca[lista]
                self.lista_colunas_filtradas.append(dataframe_deca)

            if re.search('PRAZO_FINAL.?|PRAZO.?|PRAZO FIN.?', lista, re.IGNORECASE):
                dataframe_deca[lista]
                self.lista_colunas_filtradas.append(dataframe_deca)

            if re.search('Cen.?', lista, re.IGNORECASE):
                dataframe_deca[lista]
                self.lista_colunas_filtradas.append(dataframe_deca)

    def dataframe_deca(self):

        deca_df = pd.concat(self.lista_colunas_filtradas)

        deca_df.drop_duplicates(subset='Nº do material')

        deca_df = deca_df[deca_df.loc[:, 'Cen.'].astype(str).str.contains('Jundiaí')]
        deca_df.loc[:, 'EST DISP'] = deca_df.loc[:, 'EST DISP'].astype(str)
        deca_df.loc[:, 'EST DISP'].apply(lambda k: converte_float(k))
        deca_df.loc[:, 'EST DISP'].apply(lambda k: filtrar_estoques(k))

        deca_df = deca_df[deca_df.loc[:, 'EST DISP'] != '0']
        deca_df.drop_duplicates(subset=['Cen.', 'Nº do material', 'Texto breve material'])
        deca_df = deca_df[['Nº do material', 'EST DISP', 'PRAZO_FINAL']]

        return deca_df

    # executa consulta Hauszmapa \Marca Deca
    @staticmethod
    def select_hausz_mapa_deca():
        with db.engine.connect() as conn:
            exec = (text("""SELECT DISTINCT brand.Marca,basico.[IdProduto],basico.[SKU]
                    ,basico.[NomeProduto],basico.[IdMarca]
                    FROM [HauszMapa].[Produtos].[ProdutoBasico] as basico
                    JOIN Produtos.Marca as brand
                    on brand.IdMarca = basico.IdMarca
                    WHERE brand.Marca like '%Deca%'""")).all()
            exec_deca = conn.execute(exec).all()

            for items in exec_deca:
                dict_items = {

                    'MARCA': items[0],
                    'IDPRODUTO': items[1],
                    'SKU': items[2],
                    'NOMEPRODUTO': items[3],
                    'IDMARCA': items[4]}

                yield dict(dict_items.items())

    @staticmethod
    def excel_log():
        filename = 'deca__teste_' + str(datetime.today().strftime('%Y-%m-%d %H:%M').split()[0] + '.xlsx')
        return filename

        # Chama função de consulta faz merge com dataframe deca e devolve um arquivo com as informações

    def merge_dataframe(self):
        self.reader_excel_file()
        self.unifica_dataframes()
        df_deca = self.dataframe_deca()
        deca_hauszmapa = self.select_hausz_mapa_deca()
        deca_dicts = pd.DataFrame(deca_hauszmapa)

        merge_deca = pd.merge(deca_dicts, df_deca, left_on='SKU', right_on='Nº do material', how='left')

        # merge_deca = merge_deca[['SKU','Marca', 'IdProduto','EST DISP', 'PRAZO_FINAL','IdMarca']]

        merge_deca = merge_deca.dropna()

        merge_deca = merge_deca.drop_duplicates(subset='SKU')

        name = self.excel_log()
        merge_deca.to_excel(self.log + name)
