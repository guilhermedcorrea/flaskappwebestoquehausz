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

  
class QuickStep:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def __init__(self, path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '43'
        self.prazo = float(90)
        self.Marca = 'QuickStep'
        self.path = path
        self.save_itens = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','admin','files','adminuploads')


    def converter_imgpdf(self):
        print(self.path)
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/quickstep'+ str(i) +'.jpg', 'JPEG')
            print(images[i])


    def ajuste_valores(self, strs: list) -> dict:
        lista_valores = []
        for values in strs:
            items = {}
            if re.sub(r'\s+', ' ', values):
                valores = values.strip().split()
                for val in valores:

                    try:
                        # skus
                        if re.search(r'[1-9]\d{1,5}', val):
                            cont = len(val)
                            if cont <= 8 and cont >= 3 and val != '100' and val != '500' and val != '100m' and val != '500m' and val != '<500m?':
                                items['SKU'] = str(val).replace("["
                                                                , "").replace("[", "").replace("(", "").replace("(",
                                                                                                                "").replace(
                                    ",", "")
                    except:
                        items['SKU'] = 'notfound'

                    try:
                        # saldo produto e acessorio
                        if re.search(r'100|500', val):
                            if '500' in val:
                                items['SALDO'] = float(val)

                            if '100' in val:
                                items['ACESSORIO'] = float(val)
                    except:
                        items['SALDO'] = float(0)
                        items['ACESSORIO'] = float(0)

                    try:
                        # datas
                        if re.search(r'\d{2}\/\d{2}\/\d{4}', val):
                            items['DATAS'] = val

                    except:

                        items['DATAS'] = 'notfound'

            lista_valores.append(items)

        return lista_valores

    def reader_imagem(self) -> dict:

        imgs = os.listdir(self.imagem)
        for im in imgs:
            if 'quickstep' in im:
                img = cv2.imread(os.path.join(self.imagem, im))
                # imagemgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) #Convertendo para rgb
                imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertendo para rgb
                texto = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                valor = texto.split("\n")

                remov_espacos = list(filter(lambda k: len(k.strip()) > 0, valor))
                dicts = self.ajuste_valores(remov_espacos)
                for dic in dicts:
                    dict_quick = {}
                    cont = len(dic)
                    if cont > 2:
                        try:
                            dict_quick['SKU'] = dic['SKU'],
                        except:
                            dict_quick['SKU'] = 0

                        try:
                            dict_quick['SALDO'] = dic['SALDO'],
                        except:
                            dict_quick['SALDO'] = 0

                        try:
                            dict_quick['ACESSORIO'] = dic['ACESSORIO'],
                        except:
                            dict_quick['ACESSORIO'] = 0

                        try:
                            dict_quick['DATA'] = self.dataatual,
                        except:
                            dict_quick['DATA'] = 'notfound'

                        dict_quick['IDMARCA'] = self.idmarca,
                        try:
                            dict_quick['MARCA'] = self.Marca,
                        except:
                            dict_quick['MARCA'] = 'notfound'

                        try:
                            dict_quick['PRAZO'] = self.prazo,
                        except:
                            dict_quick['PRAZO'] = 0

                        try:
                            dict_quick['DATAS'] = dic['DATAS']
                        except:
                            dict_quick['DATAS'] = 'notfound'

                        self.lista_produtos.append(dict_quick)

        return self.lista_produtos


    def dict_writer(self):
        try:
            filename = 'quickstep' + '_' + self.dataatual .split()[0] + '.csv'
            with open(self.save_itens +filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.lista_produtos[1])
                writer.writeheader()
                for row in self.lista_produtos:
                    writer.writerow(row)
        except:
            print("erro csv log quickstep")


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
            print("erro deleta arquivos quickstep")

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
            print("erro deletar files quickstep")
