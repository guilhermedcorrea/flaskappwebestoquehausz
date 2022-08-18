from itertools import zip_longest
import os
import sys
import pytesseract
from PIL import Image
from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError)
import cv2
import numpy as np
import re
import pandas as pd
from datetime import datetime
import pytesseract
from config import UPLOADFOLDER
import os
import csv
from flask import current_app



class Gaudi:
    def __init__(self, path):
        pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '27'
        self.save_itens = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','admin', 'files','adminuploads')

    def converter_imgpdf(self):
     
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/gaudi'+ str(i) +'.jpg', 'JPEG')
            print(images[i])

    def ajuste_referencias(self, listas):
        lista_dicts = []
        for lista in listas:
            valor = str(lista).split(" ")
            remov_espacos = list(filter(lambda k: len(k.strip()) > 0, valor))
            cont = len(remov_espacos)
            if cont > 5:
                dict_values = {}
                saldo = remov_espacos[-3].replace(".", "")
                sku = str(remov_espacos[0]).strip() + '1'
                try:
                    dict_values['SKU'] = sku
                except:
                    dict_values['SKU'] = 'valornaoencontrado'

                try:
                    dict_values['SALDO'] = float(saldo)
                except:
                    dict_values['SALDO'] = float(0)

                try:
                    dict_values['IDMARCA'] = self.idmarca
                except:
                    print("error")

                dict_values["PRAZO"] = 'Definido pelo fabricante'
                dict_values['MARCA'] = 'Gaudi'

                lista_dicts.append(dict_values)

        return lista_dicts

    def reader_imagem(self):
        try:
            lista_dicts_saldos = []
            imgs = os.listdir(self.imagem)

            for im in imgs:
                if 'gaudi' in im:

                    img = cv2.imread(os.path.join(self.imagem, im))
                    # imagemgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) #Convertendo para rgb
                    imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertendo para rgb
                    texto = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                    valor = texto.split("\n")
                    dicts = self.ajuste_referencias(valor)
                    for dic in dicts:
                        lista_dicts_saldos.append(dic)

            return lista_dicts_saldos
        except:
            print("erro imagem gaudi")


#essa função sera descontinuada
    def create_dataframe(self):
        try:
            listas = self.reader_imagem()
            print(listas)

            data = pd.DataFrame(listas)

            data['SKU'].fillna(0, inplace=True)

            data['SALDO'].fillna(0, inplace=True)
            data['SALDO'] = data['SALDO'].astype(float)
            data.drop(data.loc[data['SALDO'] == 'valornaoencontrado'].index, inplace=True)
            data = data.sort_values('SALDO', ascending=False).drop_duplicates('SKU').sort_index()

            # data.to_excel('D:\\hauszbi\\uploadarquivos\\logs\\gaudi.xlsx')
            jsons = data.to_dict('records')

            return jsons
        except:
            print("erro dataframe Gaudi")

    def dict_writer(self):
        try:
            filename = 'Gaudi' + '_' + self.dataatual .split()[0] + '.csv'
            with open(self.save_itens +filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.lista_produtos[1])
                writer.writeheader()
                for row in self.lista_produtos:
                    writer.writerow(row)
        except:
            print("erro csv log Gaudi")


    @staticmethod
    def delete_upload_files():
        try:
            files = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
         
            for file in files:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads',file)
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deleta arquivos Gaudi")

    @staticmethod
    def delete_image_files():
        try:
            images =os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
            path2 = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
            for file in images:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(path2, file)
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deletar files Gaudi")
