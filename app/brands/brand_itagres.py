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




class Itagres:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def __init__(self, path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '37'
        self.path = path
        self.save_itens = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','admin','files','adminuploads')

   
    def converter_imgpdf(self):
     
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/itagres'+ str(i) +'.jpg', 'JPEG')
            print(images[i])


    def filtrar_skus(self, skus):
        lista_dicts = []
        for sku in skus:
            valor = sku.split("\n")
            for val in valor:
                dict_items = {}
                try:
                    if re.search('[0-9]{1,3},[0-9]{1,2}', val, re.IGNORECASE):
                        valor = val.split(" ")
                        dict_items['CODIGO'] = valor[0]
                        dict_items['SALDO'] = valor[-1]
                        dict_items['IDMARCA'] = self.idmarca
                        lista_dicts.append(dict_items)
                except:
                    dict_items['CODIGO'] = 'valornaoencontrado'
                    dict_items['SALDO'] = '0'
                    lista_dicts.append(dict_items)

        return lista_dicts

    def converte_float(self, digitos):
        lista_dicts = []
        try:
            for digito in digitos:
                sku = digito['CODIGO']
                saldo = digito['SALDO']
                if re.search('[0-9]{1,4},[0-9]{1,2}', saldo, re.IGNORECASE):
                    dict_saldos = {}
                    valor = str(saldo).replace(".", "").replace(",", ".").strip()
                    dict_saldos["SALDO"] = valor
                    dict_saldos["SKU"] = str(sku).strip().split("—")[0].strip()
                    dict_saldos["PRAZO"] = 'Prazo do Fabricante'
                    dict_saldos['DATA'] = self.dataatual
                    dict_saldos['IDMARCA'] = self.idmarca
                    lista_dicts.append(dict_saldos)
            return lista_dicts
        except:
            print("error")

    def ajuste_saldos(self, saldos):
        ajustados = []
        try:
            for saldo in saldos:
                try:
                    if re.search('[0-9]{1,5}\.[0-9]{1,2}', saldo, re.IGNORECASE):
                        ajustados.append(float(saldo))
                    else:
                        ajustados.append('naotem')
                except:
                    ajustados.append('naotem')
            return ajustados
        except:
            print("error")

    def ajuste_skus(self, skus):
        lista_skus = []
        try:
            for sku in skus:
                try:
                    valor = str(sku).strip()
                    if re.search('[0-9]{1,5}[A]', valor, re.IGNORECASE):
                        lista_skus.append(valor)
                    else:
                        lista_skus.append('naotem')
                except:
                    lista_skus.append('naotem')
            return lista_skus
        except:
            print("error")

    def imagem_reader(self) -> None:
        tesseract_language = "por"
        config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        lista_dicts = []
        imgs = os.listdir(self.imagem)

        for im in imgs:
            try:
                img = cv2.imread(os.path.join(self.imagem, im))

                imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertendo para rgb
                texto = pytesseract.image_to_string(imagemgray, config=config)
                texto = texto.split("\n")
                remov = [x for x in texto if x != '' if x != ' ']
                saldos = self.filtrar_skus(remov)

                digitos = self.converte_float(saldos)
                for digi in digitos:
                    lista_dicts.append(digi)

            except:
                print("Erro leitura imagem")

        data = pd.DataFrame(lista_dicts)

        data['SALDO'] = self.ajuste_saldos(data['SALDO'])
        data['SKU'] = self.ajuste_skus(data['SKU'])
        data.drop(data.loc[data['SALDO'] == 'naotem'].index, inplace=True)
        data = data.sort_values('SALDO', ascending=False).drop_duplicates('SKU').sort_index()
        data['MARCA'] = 'Itagres'
        jsons = data.to_dict('records')

        return jsons



    def dict_writer(self):
        try:
            filename = 'Itagres' + '_' + self.dataatual .split()[0] + '.csv'
            with open(self.save_itens +filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.lista_produtos[1])
                writer.writeheader()
                for row in self.lista_produtos:
                    writer.writerow(row)
        except:
            print("erro csv log Itagres")


    @staticmethod
    def delete_upload_files():
        try:
            files = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
         
            for file in files:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(current_app.config['UPLOAD_PATH'], file)
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deleta arquivos Itagres")

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
            print("erro deletar files Itagres")
