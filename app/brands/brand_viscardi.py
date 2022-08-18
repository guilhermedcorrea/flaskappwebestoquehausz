import os
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import re
import pandas as pd
from datetime import datetime
import csv
from flask import current_app
from config import UPLOADFOLDER
from itertools import groupby

class Viscardi:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    def __init__(self,path):
        self.config= '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '21'
        self.listadicts = []

    def converter_imgpdf(self):
        print('arquivo funcao viscardi',self.path)

        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/viscardi'+ str(i) +'.jpg', 'JPEG')
            print(images[i])
    
    def search_files(self):
        imagem = [x for x in os.listdir(self.imagem) if 'viscardi']
        return imagem
    
    def get_referencias(self, sku):
        return str(sku['SKU'].strip())


    def reader_imagem(self):
        lista_produtos = []
        search_valores = re.compile(r'\s\d+\s\d+\,\d+')
        imagens = self.search_files()
        try:
            for imagem in imagens:
                if 'viscardi' in imagem:
                    file = cv2.imread(os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens',imagem))
                    
                    imagemgray = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)

                    texto = pytesseract.image_to_string(imagemgray, lang= self.tesseract_language,config=self.config)
                
                    remove_esp = re.sub(r'\n',' ',texto)
                    remove_esps = re.sub(r'\s+',' ',remove_esp)
                
                    valores  = search_valores.findall(remove_esps)
                    for valor in valores:
                        dict_itens = {}
                        valor = str(valor).strip().split(' ')
                        sku = 'Viscardi-'+str(valor[0])
                        saldo = float(str(valor[-1]).strip().replace(",","."))
                        dict_itens['SKU'] = sku
                        dict_itens['SALDO'] = saldo
                        dict_itens['DATA'] = self.dataatual
                        dict_itens['IDMARCA'] = self.idmarca

                        lista_produtos.append(dict_itens)
                     
                    
        except:
            print("erro reader imagem")

        return lista_produtos
    

