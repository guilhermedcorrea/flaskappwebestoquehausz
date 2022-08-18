
import os
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
import cv2
import re
from datetime import datetime
from itertools import zip_longest
import itertools
import pandas as pd



class Itagres:
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    def __init__(self):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "eng"
        self.lista_produtos = []
        self.imagem =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\imagens\\'
        self.pdffile =  r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\pdffiles\\Itagres 17.08.pdf'
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '37'

    def converter_imgpdf(self):
        images = convert_from_path(self.pdffile, 200, poppler_path=r'C:\\Users\\Guilherme\\Pictures\\readerpdf\\poppler-0.68.0\\bin')
        for i in range(len(images)):
            images[i].save(self.imagem+r'\itagres'+ str(i) +'.jpg', 'JPEG')

    def search_files(self):
        imagem = [x for x in os.listdir(self.imagem) if 'viscardi']
        return imagem


    def reader_imagem(self):
        lista_dicts = []
        imagens = self.search_files()
        try:
            for im in imagens:
                if 'itagres' in im:
                    img = cv2.imread(os.path.join(self.imagem,im))
                    imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) #Convertendo para rgb
                    texto = pytesseract.image_to_string(imagemgray
                        ,lang= self.tesseract_language,config= self.config)
                                                    
                    texto = texto.split("\n")
                    for x in texto:
                        dict_items = {}
                        strs = re.sub('\s+|[|]|[MONOP.]|[RET.]',' ', x)
                        remov_esps = re.sub('\s+',' ', strs)
                        valores = remov_esps.strip().split()
                        try:
                            sku = str(valores[0]).strip()
                            dict_items['SKU'] = sku
                        
                        except:
                            dict_items['SKU'] = 'notfound'
                            
                        try:
                            saldos = str(valores[-1]).replace(",",".").strip()
                            saldos = float(saldos)
                            dict_items['SALDOS'] = saldos
                          
                        except:
                            dict_items['SALDOS'] = float(0)

                        dict_items['IDMARCA'] = self.idmarca
                        
                        print(dict_items)
                        
   
        except:
            pass
        

     
itagres = Itagres()
#itagres.converter_imgpdf()
itagres.reader_imagem()
