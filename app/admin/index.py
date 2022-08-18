from flask import Blueprint, redirect, render_template, url_for
from ..controllers.controllers_prazos import Brands
from datetime import datetime
from ..controllers.controllers_admin_files import retorna_monitoramento_precos,retorna_filtro_marcas,retorna_concorrentes,retorna_concorrente_sku,retorna_menor_preco,retorna_maior_preco,resumo_produto,resumo_preco_info
from sqlalchemy import text
from flask_sqlalchemy import SQLAlchemy


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
    

    return render_template('dashboard.html', produtos = produtos, brands = brands, estoques = estoque_atual)



@index.route("/monitoramentodeprecos/<int:page>",methods=['GET','POST'])
def precos(page=1):
  
    brands = retorna_filtro_marcas()
    seller = retorna_concorrentes()

    lista_dicts = []

    with db.engine.connect() as conn:

        exec = (text("""
                DECLARE @PageNumber AS INT
                DECLARE @RowsOfPage AS INT
                SET @PageNumber= {}
                SET @RowsOfPage= 10
                SELECT SELLERS.[paginaprodutoseller],SELLERS.[paginaprodutogoogle] ,SELLERS.[nomeproduto],SELLERS.[nomeseller]
                ,SELLERS.[eanreferebcia]  ,SELLERS.[precoprodutoseller] ,SELLERS.[marcaprodutoseller]
                ,SELLERS.[idmarcahausz] ,SELLERS.[categoriahausz] ,SELLERS.[idprodutohausz],psaldo.DataAtualizado,
                SELLERS.[skuhausz],SELLERS.[seller]
                ,pbasico.SaldoAtual,estoq.NomeEstoque,SELLERS.[precoprodutoseller]-ppreco.Preco as 'diferenca',ppreco.Preco

                FROM [HauszMapaDev2].[dbo].[SellersPrices] AS SELLERS 
                JOIN [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
                ON pbasico.SKU = SELLERS.skuhausz
                JOIN [HauszMapaDev2].[Estoque].[Estoque] as estoq
                ON estoq.IdEstoque = pbasico.EstoqueAtual
                JOIN [HauszMapaDev2].[Produtos].[ProdutoPreco] as ppreco
                ON ppreco.SKU = pbasico.SKU
                JOIN [HauszMapa].[Produtos].[ProdutosSaldos] as psaldo
                ON psaldo.SKU = pbasico.SKU
                where ppreco.IdUnidade = 1
                ORDER BY SELLERS.[idprodutohausz],psaldo.DataAtualizado DESC
                OFFSET (@PageNumber-1)*@RowsOfPage ROWS
                FETCH NEXT @RowsOfPage ROWS ONLY""".format(page)))
        exec_produtos = conn.execute(exec).all()
        for produtos in exec_produtos:

            dict_items = {
                    "paginaprodutoseller":produtos['paginaprodutoseller'],
                    "paginaprodutogoogle":produtos['paginaprodutogoogle'],
                    "nomeproduto":produtos['nomeproduto'],
                    "nomeseller":produtos['nomeseller'],
                    "idmarcahausz":produtos['idmarcahausz'],
                    "categoriahausz":produtos['categoriahausz'],
                    "idprodutohausz":produtos['idprodutohausz'],
                    "DataAtualizado":produtos['DataAtualizado'],
                    "skuhausz":produtos['skuhausz'],
                    "seller":produtos['seller'],
                    "Preco":produtos['Preco'],
                    "SaldoAtual":produtos['SaldoAtual'],
                    "precoprodutoseller":produtos['precoprodutoseller'],
                    "NomeEstoque":produtos['NomeEstoque'],
                    "diferenca":round(produtos['diferenca'],2),
                    "eanreferebcia":produtos['eanreferebcia'],
                    "marcaprodutoseller:":produtos['marcaprodutoseller']
                }
            lista_dicts.append(dict_items)
   
    return render_template("seller.html", page=page, produtos=lista_dicts, marcas=brands, sellers = seller)


@index.route("/monitoramentodeprecos/<sku>",methods=['GET','POST'])
def retorna_prices_sku(sku):
    sellers = retorna_concorrente_sku(sku)
    menor = retorna_menor_preco(sku)
    maior = retorna_maior_preco(sku)
    resumproduto = resumo_produto(sku)
    resumopreco = resumo_preco_info(sku)
    
    return render_template('produtounico.html', skuproduto=sku, concorrentes=sellers
    ,maior=maior, menor=menor,reusmoprodutoseller=resumproduto, precoproduto=resumopreco)


@index.route("/produtosaldosgeral",methods=['GET','POST'])
def retorna_all_produto_saldo():
    return "teste"


@index.route("/produtosaldos/<sku>",methods=['GET','POST'])
def retorna_produtos_saldos_sku(sku):
    print('skuproduto',sku)
    resumopreco = resumo_preco_info(sku)
    resumprodutoss = resumo_produto(sku)

    return render_template('atualizacaoporsku.html', resumoproduto = resumopreco,detalhes = resumprodutoss)


def retorna_seller():
    return "teste"