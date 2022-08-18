
'''
from base64 import encode
import pandas as pd
import re
import os
import json

from config import UPLOADFOLDER
import os

PDF_FILE = UPLOAD_FOLDER = os.path.join(UPLOADFOLDER, 'flaskapprefatorado', 'uploads_files', 'excel_files')
IMAGEM_FILE = UPLOAD_FOLDER = os.path.join(UPLOADFOLDER, 'flaskapprefatorado', 'uploads_files', 'imagens')


class PortoFerreira:
    def __init__(self, path, dataatual) -> None:
        self.path = path
        self.dataatual = dataatual

    def seleciona_colunas(self, data) -> pd:
        lista_dfs = []

        lista_colunas = data.columns

        for listas in lista_colunas:
            if re.search('SKU.?|Produto.?|Tamanho.?', listas, re.IGNORECASE):
                skus = data[listas]
                lista_dfs.append(skus)

            elif re.search('Disp.?|Saldo.?|Estoque.?', listas, re.IGNORECASE):
                saldos = data[listas]
                lista_dfs.append(saldos)

        finall_df = pd.concat(lista_dfs, axis=1)
        return finall_df

    def ajuste_sku(self, skus) -> list:
        lista_skus = []
        for sku in skus:
            try:
                valor = str(sku)
                ref = valor[:-1] + 'PF'
                lista_skus.append(ref)
            except:
                lista_skus.append('valorinvalido')

        return lista_skus

    def converte_floats(self, saldos) -> float:
        lista_saldos = []
        for saldo in saldos:
            try:
                valor = str(saldo).replace('nan',
                                           '0').replace('NaN', '0')
                num = float(valor)
                lista_saldos.append(num)
            except:
                print("erro saldo")
                lista_saldos.append(float(0))

        return lista_saldos

    def reader_excel(self) -> dict:

        dataporto = pd.read_excel(self.path)

        lista_colunas = dataporto.columns

        for lista in lista_colunas:
            if re.search('SKU.?|Produto.?|Tamanho.?|Produto?', lista, re.IGNORECASE):
                dataporto[lista].fillna(method='ffill', inplace=True)

        portodf = self.seleciona_colunas(dataporto)
        portodf.iloc[:, [0]] = portodf.iloc[:, [0]].apply(lambda x: self.ajuste_sku(x))
        portodf.iloc[:, [1]] = portodf.iloc[:, [1]].apply(lambda x: self.converte_floats(x))
        portodf['PRAZO'] = 'Prazo do fabricante'
        portodf['MARCA'] = 'Porto Ferreira'
        portodf['DATA'] = self.dataatual
        portodf.rename(columns={'Previsão*': 'SKU', 'Produto Disponivel': 'SALDO'}, inplace=True)
        try:
            portodf.rename(columns={'Produto': 'SKU', 'Disponível': "SALDO"}, inplace=True)
            portodf['SKU'] = portodf['SKU'].apply(lambda x: str(x).replace(".PF", "PF"))
        except:
            print("Error")

        dataporto = portodf[['PRAZO', 'MARCA', 'DATA', 'SKU', 'SALDO']]
        # dataporto.to_excel(FILE + '\\logs\\' + self.path)
        jsons = dataporto.to_json(orient="records")
        values = json.loads(jsons)
        print(values)

        return values

'''