import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import re
from datetime import datetime
import os
import itertools
import pandas as pd
from itertools import groupby, count
from collections import Counter

class Viscardi:
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    def __init__(self):
        self.config= '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.imagem =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\imagens\\'
        self.pdffile =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\pdffiles\\VISCARDI.pdf'
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '21'
        self.listadicts = []

    def converter_imgpdf(self):

        images = convert_from_path(self.pdffile, 200, poppler_path=r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\poppler-0.68.0\\bin')
        for i in range(len(images)):
            images[i].save(self.imagem+r'\viscardi'+ str(i) +'.jpg', 'JPEG')
    
    
    def search_files(self):
        imagem = [x for x in os.listdir(self.imagem) if 'viscardi']
        return imagem
    
    def get_referencias(self, sku):
        return str(sku['SKU'].strip())


    def reader_imagem(self):
        search_valores = re.compile(r'\s\d+\s\d+\,\d+')
        imagens = self.search_files()
        try:
            for imagem in imagens:
                file = cv2.imread(os.path.join(self.imagem,imagem))
                
                imagemgray = cv2.cvtColor(file, cv2.COLOR_BGR2RGB)

                texto = pytesseract.image_to_string(imagemgray, lang= self.tesseract_language,config=self.config)
                valores = texto.split('\n')
                for valor in valores:
                    remov = re.sub('[A-Z]+\s+[A-Z]|\s+',' ', valor)
                    remov = remov.strip().split(" ")
                    cont = len(remov)
                    if cont >1:
                        dict_items = {}
                        
                        sku = remov[-2]
                        saldo = remov[-1]
                        try:
                            dict_items['SKU'] = str('Viscardi-') + str(sku).strip()
                        except:
                            dict_items['SKU'] = 'notfound'

                        try:
                            num = str(saldo).replace(',','.').strip()
                            dict_items['SALDO'] = round(float(num),2)
                        except:
                            dict_items['SALDO'] = float(0)

                       # dict_items['IDMARCA'] = self.idmarca
                        self.lista_produtos.append(dict_items)
                       
        except:
            pass
        return self.lista_produtos
    

    def group_by(self):
        key = lambda d: d['SKU']

        SALDO = []
        for sku,grps in groupby(sorted(self.lista_produtos, key=key), key=key):

            c = Counter()
            for grp in grps:
                grp.pop('SKU')
                c += Counter(grp)

            SALDO.append(dict(c, sku=sku))
        print(SALDO)



viscardi = Viscardi()
viscardi.converter_imgpdf()
viscardi.reader_imagem()
viscardi.group_by()




