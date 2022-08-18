from pdf2image import convert_from_path, convert_from_bytes
from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError)
from config import UPLOADFOLDER
import os
import pytesseract
import cv2
import re
import pandas as pd
from datetime import datetime
import csv
from itertools import zip_longest
import pandas as pd


class Elizabeth:
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

    def __init__(self, path):
        self.config = '--psm 4  -c preserve_interword_spaces=1 tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.[]|,,.~â ÃÂç'
        self.tesseract_language = "por"
        self.lista_produtos = []
        self.path = path
        self.imagem = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads','imagens')
        self.pdffile = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.idmarca = '14'
        self.save_itens = os.path.join(UPLOADFOLDER, 'flaskapprefatorado','app','admin','files','adminuploads')



    def converter_imgpdf(self):
     
        images = convert_from_bytes(open(self.path, 'rb').read())

        for i in range(len(images)):
            images[i].save(self.imagem+'/elizabeth'+ str(i) +'.jpg', 'JPEG')
            print(images[i])

    def reader_imagem(self):
        
        imagens = os.listdir(self.imagem)

        lista_saldos = []
        for imagem in imagens:
            if 'elizabeth' in imagem:
               
                img = cv2.imread(os.path.join(self.imagem,imagem))
                imagemgray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                valores = pytesseract.image_to_string(imagemgray, lang=self.tesseract_language, config=self.config)
                valores = valores.split("\n")
                remov_blank = list(filter(lambda k: len(k.strip()) >0, valores))
           
                for val in remov_blank:
                    dict_items = {}

                    valor = val.split(" ")
                    try:
                        valores = re.sub("\n"," ",str(valor))
                    except:
                        print("erro")

                    try:
                        referencia = re.findall(r"\d{7,20}\W{3}?\d?", valores)
                        dict_items['SKU'] = str(referencia).replace('["'
                        ,'').replace('"]','').replace('"','').replace('"'
                        ,'').replace(',",','').replace('"','').replace(" ","").replace('",','').strip()
                        
                    except:
                        dict_items['SKU'] = 'notfound'
                        print("erro referencia")
                    try:
                        saldos = re.findall(r"\d+?\.?\d+\,\d+", valores)
                        dict_items['SALDO'] = float(str(saldos[-1].replace(",",".")))

                    except:
                        print("erro saldo")

                        dict_items['SALDO'] = 0

                    self.lista_produtos.append(dict_items)

                    print(dict_items)
        
        return self.lista_produtos

                    
        #data = pd.DataFrame(lista_saldos)
        #print(data)
        




