from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import text

db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


class DashAdmin:
    def __init__(self, bit):
        self.data = str(datetime.today().strftime('%Y-%m-%d %H:%M'))
        self.bit = bit

    def resumo_produtos(self, bit):
        lista_dicts = []

        query_atualizados = db.engine.execute("""
            SELECT DISTINCT  TOP(5) pmarca.Marca,pbasico.[IdProduto],pbasico.[SKU]
            ,pbasico.[NomeProduto],pbasico.[SaldoAtual],pestoque.NomeEstoque, psaldo.Quantidade
            ,format(psaldo.DataAtualizado, 'd', 'pt-BR') as 'dataatualizado',psaldo.DataAtualizado,
            CASE 
                WHEN format(psaldo.DataAtualizado, 'd', 'pt-BR') = format(getdate(), 'd', 'pt-BR') THEN 'Atualizado'
                WHEN format(psaldo.DataAtualizado, 'd', 'pt-BR') <> format(getdate(), 'd', 'pt-BR') THEN 'NaoAtualizado'
            ELSE 'Verificar'
            END 'StatusMarcas'
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            JOIN [HauszMapa].[Produtos].[Marca] AS pmarca
            on pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Estoque].[Estoque] AS pestoque
            on pestoque.[IdEstoque] = pbasico.EstoqueAtual
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            on psaldo.SKU = pbasico.SKU
            WHERE pestoque.bitCrossDocking  like '%{}%' and psaldo.Quantidade > 0
            order by psaldo.DataAtualizado desc""".format(bit))
        for query_dict in query_atualizados:
            dict_itens = {

                'IdProduto': query_dict[1],
                'Marca': query_dict[0],
                'SKU': query_dict[2],
                'NomeProduto': query_dict[3],
                'Quantidade': float(query_dict[4]),
                'Verificar': query_dict[9],
                'Data': query_dict[7]}

            lista_dicts.append(dict_itens)
        cont = len(lista_dicts)

        return lista_dicts

    @staticmethod
    def nao_atualizados_dia():
        lista_dicts = []
        somados = []
        with db.engine.connect() as conn:
            exec = (text(""" 
                SELECT pmarca.Marca ,COUNT(pbasico.[SKU]) AS 'QUANTIDADEPRODUTOS'
                FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
                JOIN [HauszMapa].[Produtos].[Marca] as pmarca
                ON pmarca.IdMarca = pbasico.IdMarca
                JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
                ON psaldo.SKU = pbasico.SKU
                WHERE  pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
                WHERE convert(VARCHAR, psaldo.DataAtualizado
                , 23) <= CONVERT(DATE, DATEADD(DAY, -1, GETDATE())) AND pbasico.BitAtivo = 1)
                GROUP BY pmarca.Marca"""))

            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_items = {
                    'MARCA': produto[0],
                    'SKUS': int(produto[1])

                }
                somados.append(produto[1])

                lista_dicts.append(dict_items)

        somar = sum(somados)
        somatot = int(somar)

        return somatot

    @staticmethod
    def cont_produtos_nao_atualizado():
        lista_dicts = []
        query_atualizados = db.engine.execute("""
            SELECT pbasico.[SKU]
            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            WHERE  pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
            WHERE convert(VARCHAR, psaldo.DataAtualizado
            , 23) <= CONVERT(DATE, DATEADD(DAY, -1, GETDATE())) AND pbasico.BitAtivo = 1)
                
            """)

        for dicts in query_atualizados:

            lista_dicts.append(dicts)

        cont = len(lista_dicts)
        return cont

    @staticmethod
    def cont_produtos(bit):
        lista_dicts = []
        query_atualizados = db.engine.execute("""
            SELECT pbasico.NomeProduto,pbasico.SaldoAtual,psaldos.[SKU]
            ,psaldos.[IdMarca],psaldos.[Quantidade],Cast(psaldos.[DataAtualizado] as date) AS dataatual
            FROM [HauszMapa].[Produtos].[ProdutosSaldos] as psaldos
            join [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            on pbasico.SKU = psaldos.SKU
            JOIN [HauszMapa].[Estoque].[Estoque] AS pestoque
            on pestoque.[IdEstoque] = pbasico.EstoqueAtual
            WHERE pestoque.bitCrossDocking = 1
            """.format(bit))
        for dicts in query_atualizados:
            dict_itens = {
                'id': dicts[0]}
            lista_dicts.append(dict_itens)
        cont = len(lista_dicts)
        return cont

    @staticmethod
    def produto_estoque():
        lista_dicts = []
        estoque_disp = db.engine.execute("""SELECT pbasico.NomeProduto,pbasico.SaldoAtual,psaldos.[SKU]
            ,psaldos.[IdMarca],psaldos.[Quantidade],Cast(psaldos.[DataAtualizado] as date) AS dataatual
            FROM [HauszMapa].[Produtos].[ProdutosSaldos] as psaldos
            join [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            on pbasico.SKU = psaldos.SKU
            JOIN [HauszMapa].[Estoque].[Estoque] AS pestoque
            on pestoque.[IdEstoque] = pbasico.EstoqueAtual
            and pestoque.bitCrossDocking = 0 and psaldos.[Quantidade] >0""")
        for estoques in estoque_disp:
            dict_itens = {
                'IdMarca': estoques[3]}
            lista_dicts.append(dict_itens)

        cont = len(lista_dicts)
        return cont


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


def retorna_filtro_marcas():
    lista_marcas = []
    with db.engine.connect() as conn:

        exec = (text(""" 
            SELECT distinct[marcaprodutoseller] 
            FROM [HauszMapaDev2].[dbo].[SellersPrices]"""))
        precossellers = conn.execute(exec).all()
        for marcas in precossellers:
            brand = {
                'Marca': marcas[0]
            }
            lista_marcas.append(brand)
    return lista_marcas


def retorna_concorrentes():
    lista_dicts = []
    with db.engine.connect() as conn:
        exec = (text("""
            SELECT DISTINCT  [nomeseller]
            FROM [HauszMapaDev2].[dbo].[SellersPrices]"""))
        precossellers = conn.execute(exec).all()
        for sellers in precossellers:
            dict_items = {
                "Seller": sellers[0]
            }
            lista_dicts.append(dict_items)

    return lista_dicts


def retorna_concorrente_sku(sku):
    lista_dicts = []
    with db.engine.connect() as conn:
        exec = (text("""  
            SELECT [paginaprodutoseller]  ,[paginaprodutogoogle] ,[nomeseller]  
            ,[precoprodutoseller] ,[seller] ,CONVERT(VARCHAR, [DataAtualizado], 23) AS DATAS
            FROM [HauszMapaDev2].[dbo].[SellersPrices]
            WHERE skuhausz = '{}'
                """.format(sku)))
        precossellers = conn.execute(exec).all()
        for sellers in precossellers:

            dicts = {
                "paginaprodutoseller":sellers['paginaprodutoseller'] ,
                "paginaprodutogoogle":sellers['paginaprodutogoogle'] ,
                "nomeseller":sellers['nomeseller'],
                "precoprodutoseller":sellers['precoprodutoseller'],
                "seller":sellers['seller'],
                "DATAS":sellers['DATAS']

            }
            print(dicts)
            lista_dicts.append(dicts)
    return lista_dicts



def retorna_maior_preco(sku):
    with db.engine.connect() as conn:
        exec = (text("""  
                SELECT top(1)[nomeseller]  
                ,MAX([precoprodutoseller])
                FROM [HauszMapaDev2].[dbo].[SellersPrices]
                WHERE skuhausz = '{}'
                GROUP BY [nomeseller]
            """.format(sku)))
        maiorpreco = conn.execute(exec).all()
        return maiorpreco
                

def retorna_menor_preco(sku):
    with db.engine.connect() as conn:
        exec = (text("""  
                SELECT [nomeseller]  
                ,[precoprodutoseller]
                FROM [HauszMapaDev2].[dbo].[SellersPrices]
                WHERE skuhausz = '{}'
                order by [precoprodutoseller] asc
            """.format(sku)))
        maiorpreco = conn.execute(exec).all()
        return maiorpreco

def resumo_produto(sku):
    lista_produtos = []
    with db.engine.connect() as conn:

        exec = (text("""  
    
                SELECT TOP(1) ESTOQ.NomeEstoque,basico.[SKU],basico. [NomeProduto] ,basico.[bitLinha]
            ,basico.[BitAtivo] ,basico.[IdSubCat],basico.[bitOmie]
            ,basico.[EstoqueAtual] ,basico.[SaldoAtual], 
            CASE
                WHEN basico.[bitLinha] = 1 THEN 'ForaDeLinha'
                WHEN basico.[bitLinha] = 0 THEN 'EmLinha'
                ELSE 'NAOAVALIADO'
            END 'STATUS',
            CASE
                WHEN basico.[BitAtivo] = 1 THEN 'Ativo'
                WHEN basico.[BitAtivo] = 0 THEN 'Inativo'
                ELSE 'NAOAVALIADO'
            END 'BIT'
            FROM [HauszMapa].[Produtos].[ProdutoBasico]  as basico
            JOIN [HauszMapa].[Estoque].[Estoque] AS ESTOQ
            ON ESTOQ.IdEstoque = basico.EstoqueAtual
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] as psaldo
            ON psaldo.SKU = basico.SKU
            WHERE basico.[SKU] = '{}'
            ORDER BY  psaldo.DataAtualizado DESC
                
        """.format(sku)))
        resumoproduto = conn.execute(exec).all()
        for produto in resumoproduto:
            dict_items = {
                "NomeEstoque":produto['NomeEstoque'],
                "SKU":produto['SKU'],
                "NomeProduto":produto['NomeProduto'],
                "STATUS":produto['STATUS'],
                "BIT":produto['BIT'],
                "EstoqueAtual":produto['EstoqueAtual'],
                "SaldoAtual":produto['SaldoAtual']
            }
            print(dict_items)
            lista_produtos.append(dict_items)
    return lista_produtos
   

def resumo_preco_info(sku):
    lista_produtos = []
    with db.engine.connect() as conn:

        exec = (text(""" 
            SELECT TOP(1) pdetalhe.Descricao,ppreco.[SKU],ppreco.[Custo]
            ,convert(VARCHAR, psaldo.DataAtualizado, 23) as 'data',psaldo.Quantidade
            ,ppreco.[PrecoMinimo],ppreco.[Preco],pdetalhe.FatorMultiplicador
            ,pdetalhe.FatorMultiplicador,pdetalhe.FatorUnitario,pbasico.SaldoAtual, pbasico.NomeProduto
            FROM [HauszMapa].[Produtos].[ProdutoPreco] as ppreco
            JOIN [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
            ON pbasico.SKU = ppreco.SKU
            join [HauszMapa].[Produtos].[ProdutoDetalhe] as pdetalhe
            ON pdetalhe.IdProduto = pbasico.IdProduto
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] as psaldo
            on psaldo.SKU = pbasico.SKU
            where ppreco.IdUnidade = 1 and pbasico.SKU = '{}'
            ORDER BY psaldo.Quantidade DESC
            """.format(sku)))
        resumoproduto = conn.execute(exec).all()
        return resumoproduto

def select_marcas():
    lista_produtos = []
    with db.engine.connect() as conn:

        exec = (text(""" SELECT [IdMarca],[Marca]      
            FROM [HauszMapa].[Produtos].[Marca]"""))
        marcas_produtos = conn.execute(exec).all()
        for marca in marcas_produtos:
            dict_marca = {}
            dict_marca['IdMarca'] = marca[0],
            dict_marca['Marca'] = marca[1]
            lista_produtos.append(dict_marca)

        return lista_produtos


def select_estoque():
    lista_dicts = []
    with db.engine.connect() as conn:
        
        exec = (text("""SELECT DISTINCT [EstoqueLocal], NomeEstoque
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as basico
            JOIN  [HauszMapa].[Estoque].[Estoque] as estoq
            ON estoq.IdEstoque = basico.EstoqueAtual"""))
        categoria_produtos = conn.execute(exec).all()
        for categoria in categoria_produtos:
            dict_items = {}
            dict_items['IdCategoria'] = categoria['EstoqueLocal'],
            dict_items['NomeEstoque'] = categoria['NomeEstoque']
            lista_dicts.append(dict_items)

    return lista_dicts
            

                    
        


