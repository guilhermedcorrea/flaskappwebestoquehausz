import re
import pandas as pd
from datetime import datetime
import os
from flask import current_app
import csv
from config import UPLOADFOLDER


class Level:
    def __init__(self, path):
        self.lista_dicts_saldos = []
        self.Marca = 'Level'
        self.dataatual = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.prazo = 90
        self.path = path
        self.idmarca = 45
        self.prefixo_marca = 'L'



    def read_excel(self):
        try:
            data = pd.read_excel(self.path)
            data.drop_duplicates()
            dicts = data.to_dict('records')

            for dic in dicts:
                dict_items = {}
                for keys, values in dic.items():

                    if re.search(r'\w[cóCÓcoCO]di.?', keys):
                        try:
                            dict_items['SKU'] = str(values).strip() + self.prefixo_marca
                        except:
                            dict_items['SKU'] = 'notfound'

                    elif re.search(r'estoque.?|saldo.?' ,keys, re.IGNORECASE):
                        try:
                            dict_items['SALDO'] = round(float(values) ,2)
                        except:
                            dict_items['SALDO'] = float(0)

                        dict_items['MARCA'] = self.Marca
                        dict_items['DATA'] = self.dataatual
                        dict_items['IDMARCA'] = self.idmarca


                    self.lista_dicts_saldos.append(dict_items)
                print(dict_items)

            return self.lista_dicts_saldos
        except:
            print("erro excel level")

    def cria_log_marca(self )-> None:
        filename = self.Marca +'_ ' +self.dataatual.split()[0 ] +'.xlsx'

        data = pd.DataFrame(self.lista_dicts_saldos)
        data.drop_duplicates()
        data.to_excel(filename)



    def dict_writer(self):
        try:
            filename = 'Level' + '_' + self.dataatual .split()[0] + '.csv'
            with open(self.save_itens +filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=self.lista_produtos[1])
                writer.writeheader()
                for row in self.lista_produtos:
                    writer.writerow(row)
        except:
            print("erro csv log Level")
   

    @staticmethod
    def delete_upload_files():
        try:
            files = os.listdir(current_app.config['UPLOAD_PATH'])
         
            for file in files:
                if '.pdf' in file or '.xlsx' in file or '.png' in file or '.jpg' in file:
                    remov = os.path.join(UPLOADFOLDER,'app','uploads') + file
                    print(remov)
                    os.remove(remov)
        except:
            print("erro deleta arquivos Level")



