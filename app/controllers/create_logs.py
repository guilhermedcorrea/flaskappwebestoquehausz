
from datetime import datetime
from functools import wraps

#funçao de ordem superior
def call_procedure_hausz_mapa(wrapped_function):
  def wrapper_function(args,*kwargs):
   
    print('geralog',kwargs['data'],kwargs['userid'], kwargs['sku'], kwargs['idmarca'], kwargs['saldo'], kwargs['prazo'])
    return wrapped_function(args,*kwargs)
  return wrapper_function
 
@call_procedure_hausz_mapa
def wrapped_function(args,*kwargs):
  print("ola", kwargs)
 
a = 10
data = str(datetime.today()).split()[0]
wrapped_function(data=data,userid = 2,sku=50,idmarca =60, saldo=20, prazo=30)



class GeralogsHauszMapa:
    def __init__(self):
        pass