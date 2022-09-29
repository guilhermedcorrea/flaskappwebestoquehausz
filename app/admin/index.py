from flask import Blueprint, redirect, render_template, url_for
from ..controllers.controllers_prazos import Brands
from datetime import datetime
from ..controllers.controllers_admin_files import (retorna_monitoramento_precos,retorna_filtro_marcas,retorna_concorrentes,retorna_concorrente_sku
,retorna_menor_preco,retorna_maior_preco,resumo_produto,resumo_preco_info,select_marcas)
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy
#from ..controllers.query_dashboard import (select_pedidos_vendas_marcas,select_grafico_marcas
#, select_media_prazo_marcas,select_marcas_perdas)


db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db



index = Blueprint('index', __name__)


@index.route('/')
def dashboard():
    

    data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
    data = str(data).split()[0].split('-')[1:]
    mesatual = str(data[0])+'/'+str(data[1])+'/'
    brand = Brands()
    produtos = brand.select_marcas()
    brands = brand.vendas_mes_marcas_hausz_mapa(mesatual)
    estoque_atual = brand.consultas_ranking_estoque_hausz()
    
    #vendas_marcas = select_pedidos_vendas_marcas()
    #saldo_marcas = select_grafico_marcas()
    #media_prazo_marcas = select_media_prazo_marcas()
    #perdas_marcas = select_marcas_perdas()


    #return render_template('dashboard.html', media_prazo_marcas = media_prazo_marcas, vendas_marcas = vendas_marcas, saldo_marcas = saldo_marcas,
    #perdas_marcas=perdas_marcas)


def retorna_filtro_marcas():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
            SELECT distinct [marcaprodutoseller] 
            FROM [HauszMapaDev2].[dbo].[SellersPrices]"""))
        precossellers = conn.execute(exec).all()
        for marcas in precossellers:
            brand = {
                'marcaprodutoseller': marcas['marcaprodutoseller'],
               
            }
            lista_marcas.append(brand)

    return lista_marcas


def retorna_filtro_sellers():
    lista_marcas = []
    with db.engine.connect() as conn:
        exec = (text(""" 
            select distinct IdSeller ,nomeseller  from
                [HauszMapaDev2].[dbo].[SellersPrices]
                """))
        sellers = conn.execute(exec).all()
        for seller in sellers:
            sellerproduto = {
                'IdSeller':seller['IdSeller'],
                'nomeseller':seller['nomeseller']
            }
            lista_marcas.append(sellerproduto)
    return lista_marcas


def retorna_monitoramento_precos(page):
    lista_produtos = []
    with db.engine.connect() as conn:

        exec = (text(""" 
            DECLARE @PageNumber AS INT
            DECLARE @RowsOfPage AS INT
            SET @PageNumber= {}
            SET @RowsOfPage= 8
            SELECT [paginaprodutoseller] ,[paginaprodutogoogle],[nomeproduto]
            ,[nomeseller] ,[eanreferebcia]  ,[precoprodutoseller]  ,[marcaprodutoseller] 
            ,[skuhausz] ,[precohausz]  ,[diferenciapreco]   ,[dataatualizado] 
            ,[seller]     
            FROM [HauszMapaDev2].[dbo].[SellersPrices]
            ORDER BY [dataatualizado] DESC
            OFFSET (@PageNumber-1)*@RowsOfPage ROWS
            FETCH NEXT @RowsOfPage ROWS ONLY
            """.format(page)))
        precossellers = conn.execute(exec).all()
        for estoques in precossellers:
            items = {
                'paginaprodutoseller': estoques[0],
                'paginaprodutogoogle': estoques[1],
                'nomeproduto': estoques[2],
                'nomeseller': estoques[3],
                'eanreferebcia': estoques[4],
                'precoprodutoseller': estoques[5],
                'marcaprodutoseller': estoques[6],
                'skuhausz': estoques[7],
                'precohausz': estoques[8],
                'diferenciapreco': estoques[9],
                'dataatualizado': estoques[10],
                'seller': estoques[11]
            }

            lista_produtos.append(items)
        
    return lista_produtos


@index.route("/monitoramentodeprecos/<int:page>", methods=['GET','POST'])
def produtos(page=1):
  
    propdutos = retorna_monitoramento_precos(page)
    marca = retorna_filtro_marcas()
    sellers = retorna_filtro_sellers()
    return render_template('produtos.html', page=page, produtos=propdutos, marcas=marca, sellers=sellers)


@index.route("/monitoramentodeprecos/<sku>",methods=['GET','POST'])
def retorna_prices_sku(sku):
    status = ['Ganhando','Perdendo']
    sellers = retorna_concorrente_sku(sku)
    menor = retorna_menor_preco(sku)
    maior = retorna_maior_preco(sku)
    resumproduto = resumo_produto(sku)
    resumopreco = resumo_preco_info(sku)
    
    return render_template('produtounico.html', skuproduto=sku, concorrentes=sellers
    ,maior=maior, menor=menor,reusmoprodutoseller=resumproduto, precoproduto=resumopreco,status=status)


@index.route("/produtosaldosgeral",methods=['GET','POST'])
def retorna_all_produto_saldo():
    return "teste"


@index.route("/produtosaldos/<sku>",methods=['GET','POST'])
def retorna_produtos_saldos_sku(sku):
    print('skuproduto',sku)
    resumopreco = resumo_preco_info(sku)
    resumprodutoss = resumo_produto(sku)
    

    return render_template('atualizacaoporsku.html', resumoproduto = resumopreco
    ,detalhes = resumprodutoss)


@index.route("/logalteracoes", methods=['GET','POST'])
def log_alteracoes_skus():
    pass

def retorna_seller():
    return "teste"
