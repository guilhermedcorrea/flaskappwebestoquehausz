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


#https://stackoverflow.com/questions/57567297/sum-of-key-values-in-list-of-dictionary-grouped-by-particular-key
class Elizabeth:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def __init__(self, path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.lista_produtos = []
        self.path = 'C:\\Users\\Guilherme\\Pictures\\readerpdf\\pdffiles\\elizabeth.pdf'
        self.imagem = 'C:\\Users\\Guilherme\\Pictures\\readerpdf\\imagens\\'
    
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M')).split()[0]
        self.idmarca = '14'
   
    def converter_imgpdf(self):
        images = convert_from_path(self.path, 200, poppler_path='C:\\Users\\Guilherme\\Pictures\\readerpdf\\poppler-0.68.0\\bin')
        for i in range(len(images)):
            images[i].save(self.imagem+'elizabeth'+ str(i) +'.jpg', 'JPEG')


    def reader_imagem(self):
        imagens = os.listdir(self.imagem)
      
        lista_saldos = []
        for imagem in imagens:
            if 'elizabeth' in imagem:
                img = cv2.imread('C:\\Users\\Guilherme\\Pictures\\readerpdf\\imagens\\'+ imagem)
                imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                valores = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                valores = valores.split('\n')
                for valor in valores:
                    dict_item = {}
                    x = valor.find('0104')
                    y = valor.find('0101')
                    sep = valor[x:].split()
                    if x >0:
                        try:
                            
                            sku = sep[0]
                            saldo = sep[-1]
                            dict_item['SKU'] = sku
                            if len(saldo) <=9:
                                dict_item['SALDO'] = round(float(str(saldo).replace(".","").replace(",",".")),2)
                            else:
                                dict_item['SALDO'] = 0

                            lista_saldos.append(dict_item)
                            self.lista_produtos.append(dict_item)
                           
                        except:
                            pass

                   
                    elif y >0:
                        try:
                            sku = sep[0]
                            saldo = sep[-1]
                            dict_item['SKU'] = sku
                            if len(saldo) <= 9:

                                dict_item['SALDO'] = round(float(str(saldo).replace(".","").replace(",",".")),2)
                            else:
                                dict_item['SALDO'] = 0

                            self.lista_produtos.append(dict_item)

                        except:
                            pass



    def group_by(self):
        key = lambda d: d['SKU']
        SALDO = []
        for sku,grps in groupby(sorted(self.lista_produtos, key=key), key=key):
            c = Counter()
            for grp in grps:
                grp.pop('SKU')
                c += Counter(grp)

            SALDO.append(dict(c, sku=sku))
        return SALDO
        
       
