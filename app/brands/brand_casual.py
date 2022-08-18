from ast import Yield
from itertools import zip_longest
import os
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import re
import pandas as pd
from datetime import datetime
from flask import current_app

from config import UPLOADFOLDER


class CasualLight:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    def __init__(self):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = 30
        self.Marca = 'Casual'
        self.prazo = float(90)
        self.lista_dicts_saldos = []
        self.save_itens = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','admin','files','adminuploads')

    def converter_imgpdf(self):
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'\casual'+ str(i) +'.jpg', 'JPEG')
            print(images[i])

    def regex_sku(self, data: str) -> list:
        try:
            if re.search('\w{1,5}\d+\-\w+', data, re.IGNORECASE):
                valor = re.sub(r'\s+', ' ', data)
                new_valor = re.sub(r'\d{4}\.\d{2}\.\d{2}', '', valor)
                infos = new_valor.strip().split()
                if infos:
                    yield infos
        except:
            return 'notfound'

    def ajuste_saldos(self, kwargs: dict) -> dict:
        items = {}
        saldos = kwargs['SALDO']
        if saldos.isdigit():
            try:
                items['SALDO'] = float(saldos)
                items['SKU'] = kwargs['SKU']
            except:
                items['SALDO'] = 'notfound'
                items['SKU'] = float(0)

        elif re.search('ACI.?', saldos):
            try:
                items['SALDO'] = float(50)
                items['SKU'] = kwargs['SKU']
            except:
                items['SALDO'] = float(0)
                items['SKU'] = 'notfound'

        else:
            try:
                items['SALDO'] = float(0)
                items['SKU'] = kwargs['SKU']
            except:
                items['SALDO'] = float(0)
                items['SKU'] = 'notfound'

        return items

    def reader_imagem(self) -> dict:
        imgs = os.listdir(self.imagem)
        for im in imgs:
            try:
                if 'casual' in im:
                    img = cv2.imread(os.path.join(self.imagem, im))
                    # imagemgray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) #Convertendo para rgb
                    imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convertendo para rgb
                    texto = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                    valores = texto.split("\n")
                    for valor in valores:
                        skus = self.regex_sku(valor)
                        for sku in skus:
                            items = {}
                            items['SKU'] = sku[1]
                            items['SALDO'] = sku[-1]

                            dicts = self.ajuste_saldos(items)
                            dict_casual = {
                                'SKU': dicts.get('SKU'),
                                'SALDO': dicts.get('SALDO'),
                                'MARCA': self.Marca,
                                'IDMARCA': self.idmarca,
                                'DATA': self.dataatual,
                                'PRAZO': self.prazo
                            }

                            print(dict_casual)
                            self.lista_dicts_saldos.append(dict_casual)
            except:
                print("notfound")

    def cria_log_marca(self) -> None:
        filename = self.Marca + '_' + self.dataatual.split()[0] + '.xlsx'

        data = pd.DataFrame(self.lista_dicts_saldos)
        data.to_excel(filename)

