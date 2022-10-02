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

class Lexxa:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
    def __init__(self,path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.imagem =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\imagens\\'
        self.pdffile =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\pdffiles\\lexxa.pdf'
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '21'
        self.listadicts = []

    def converter_imgpdf(self):

        images = convert_from_path(self.pdffile, 200, poppler_path=r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\poppler-0.68.0\\bin')
        for i in range(len(images)):
            images[i].save(self.imagem+r'\lexxa'+ str(i) +'.jpg', 'JPEG')
    
    
    def search_files(self):
        imagem = [x for x in os.listdir(self.imagem) if 'lexxa']
        return imagem
    

    def reader_imagem(self):
    
        imagens = self.search_files()
  
        try:
            for imagem in imagens:
                if 'lexxa' in imagem:
                    file = cv2.imread(os.path.join(self.imagem,imagem))
                    
                    imagemgray = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)

                    texto = pytesseract.image_to_string(imagemgray, lang= self.tesseract_language,config=self.config)
                    valores = texto.split('\n')
                    for valor in valores:
                        dict_items = {}
                        valor = valor.strip().split()
                        cont = len(valor)
                        if cont >1:
                            try:
                                SKU = valor[0]
                                SKU = str(SKU).strip()
                                dict_items['SKU'] = SKU
                            except:
                                dict_items['SKU'] = 'notfound'

                            try:
                                saldo = str(valor[-1]).strip()
                                num = float(saldo)
                                dict_items['SALDO'] = num
                            except:
                                dict_items['SALDO'] = 0

                            self.lista_produtos.append(dict_items)
        
        except:
            pass
               
        return self.lista_produtos  
   
       

