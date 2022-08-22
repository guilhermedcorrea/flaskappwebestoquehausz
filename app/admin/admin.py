from unicodedata import category
from ..controllers.controllers_admin_files import DashAdmin, select_marcas, select_estoque
from ..models.hausz_mapa import (Usuarios, GrupoUsuario, ProdutosSaldos, ProdutoPrazoProducFornec, DeparaProdutos, ColetadosDiario,
                                 ProdutoDetalhe, ProdutoBasico, ProdutoMarca, ArquivosConvertidos,SellersPrices)
from ..controllers.controllers_querys import ResumoDash
from ..controllers.factory_classes import Produto
from venv import create
from flask import (Blueprint, render_template, request, redirect,
                   url_for, abort, current_app, send_from_directory, send_file, request)
from os.path import dirname, join
from flask_admin import BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from flask_login import current_user
import os
from flask_sqlalchemy import SQLAlchemy
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import Admin
from sqlalchemy import text
from werkzeug.utils import secure_filename
import os
import flask_excel as excel
from datetime import datetime
from flask_admin.base import BaseView, expose
from flask_admin.menu import MenuLink
from config import UPLOADFOLDER
from sqlalchemy import func, join
import re

from .reader_csv_file import ReaderCsv

#/home/debian/Área de trabalho/flaskapprefatorado/app/uploads
files = os.path.join(UPLOADFOLDER, 'flaskapprefatorado',
                     'app', 'admin', 'files', 'adminuploads')

adm = Blueprint('adm', __name__)
current_app.config["UPLOAD_FOLDER"] = os.path.join(UPLOADFOLDER,'flaskapprefatorado','app','uploads')
excel.init_excel(current_app)


db = SQLAlchemy()


def configure(app):
    db.init_app(app)
    app.db = db


class DefaultModelView(ModelView):
    page_size = 20

    create_modal = True
    # column_exclude_list = ['password_hash']
    column_display_pk = True
    column_searchable_list = ['SKU']
    can_view_details = True
    column_list = ['SKU', 'IdPrazos', 'PrazoEstoqueFabrica',
                   'PrazoProducao', 'PrazoOperacional', 'PrazoFaturamento', 'PrazoTotal']

    # column_default_sort = ('last_name', False)
    column_filters = [

        'SKU', 'PrazoTotal', 'PrazoProducao'

    ]
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True

    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login.login_usuario'))


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def Home(self):
        valore = 100
        produtos_crossdocking = DashAdmin(1).resumo_produtos(1)
        cont_natualizado = DashAdmin(1).cont_produtos(1)

        produtos_disponivel = DashAdmin(0).resumo_produtos(0)
        cont_estoque = DashAdmin(0).produto_estoque()

        dash = ResumoDash()
        total_marcas, dicts = dash.marcas_atualizadas_dia_atual()

        naofeito = DashAdmin.cont_produtos_nao_atualizado()

        return self.render('admin/index.html', produtosc=produtos_crossdocking, cont_natualizado=cont_natualizado, produtoe=produtos_disponivel, cont_estoque=cont_estoque, atualizado_dia_marca=total_marcas, tot_nao_feito=naofeito)
    # pass
    # def is_accessible(self):
    #   return current_user.is_authenticated


admin = Admin(current_app, name='HauszAdmin',
              template_mode='bootstrap3', index_view=MyAdminIndexView())

current_app.config['FLASK_ADMIN_FLUID_LAYOUT'] = True


class CommentView(ModelView):
    create_modal = True

class UploadfilesView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/uploads.html')

    @expose('/uploads')
    def upload_arquivos(self):
        files = os.listdir(current_app.config["UPLOAD_FOLDER"])
       

        return self.render('admin/uploads.html', files=files)

    @expose('/uploads', methods=['POST'])
    def upload_files(self):
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        print('marcaaaaaaaaaaaaaaaa',os.path.join(current_app.config["UPLOAD_FOLDER"]))
        if filename != '':
            if '.csv' in filename:
                file = uploaded_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"],'csv',filename))
               
                excel = ReaderCsv(os.path.join(current_app.config["UPLOAD_FOLDER"],'csv',filename))
                files = excel.reader_csv(os.path.join(current_app.config["UPLOAD_FOLDER"],'csv',filename))
           

            elif '.pdf' in filename:    
                files = uploaded_file.save(os.path.join(current_app.config["UPLOAD_FOLDER"],'pdf', filename))
                
                valor = str(os.path.join(current_app.config["UPLOAD_FOLDER"],'pdf', filename))
                #print('arquivo Marca', file)
                dicts = Produto(valor)
                dicts_products = dicts.retorna_marca()

            return '', 204
       
            #print('aqui salvo',os.path.join(current_app.config['UPLOAD_PATH'], filename))
        return self.render("admin/informacoesestoque.html", produtos=dicts_products)


            
    @expose('/uploads/<filename>')
    def upload(self, filename):
        filesaldo = os.path.join(UPLOADFOLDER, 'app', 'uploads', filename)

        dicts = Produto(filesaldo)

        dicts_products = dicts.retorna_marca()

        return send_from_directory(os.path.join(UPLOADFOLDER, 'app', 'uploads', filename))
        # return render_template("admin/informacoesestoque.html", produtos=dicts_products)

    @expose("/modelosaldo", methods=['GET', 'POST'])
    def export_modelo_alteracao_saldo(self):
        return excel.make_response_from_array([['SKU', 'MARCA', 'SALDO', 'PRAZO']], "xlsx", file_name="exportmodelosaldo.xlsx")


admin.add_view(UploadfilesView(name='Uploadfiles', endpoint='uploads'))


class NotificationsView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/notification.html')

    @expose('/saldofornecedoresumo', methods=('GET', 'POST'))
    def croosdocking_view(self):

        lista_dicts = []
        with db.engine.connect() as conn:
            exec = (text("""
                SELECT DISTINCT brand.[IdMarca]
                    ,brand.[Marca],COUNT(basico.SKU) AS 'QUANTIDADE'
                    , brand.BitAtivo,

                    CASE
                        WHEN brand.BitAtivo = 1 THEN 'MarcaAtiva'
                        WHEN brand.BitAtivo = 0 THEN 'MarcaInativa'
                        ELSE 'NaoAvaliado'
                    END 'STATUSMARCA'
                    FROM [HauszMapa].[Produtos].[Marca] as brand
                    JOIN [HauszMapa].[Produtos].[ProdutoBasico] as basico
                    ON basico.IdMarca r = brand.IdMarca
                    GROUP BY brand.[IdMarca], brand.[Marca],brand.BitAtivo
                            
                    """))
            saldos_crossdocking = conn.execute(exec).all()
            for saldos in saldos_crossdocking:
                dict_items = {
                    'IdMarca': saldos[0],
                    'Marca': saldos[1],
                    'QUANTIDADE': saldos[2],
                    'STATUSMARCA': saldos[4]

                }

                lista_dicts.append(dict_items)

        return self.render('admin/saldofornecedor.html', produtos=lista_dicts)

    @expose('/saldodisponivel/<int:page>', methods=('GET', 'POST'))
    def disponivel_view(self, page):
        # filtros
        marcas = select_marcas()
        estoques = select_estoque()
        lista_dicts = []
        with db.engine.connect() as conn:

            exec = (text("""
               DECLARE @PageNumber AS INT
                DECLARE @RowsOfPage AS INT
                SET @PageNumber= {}
                SET @RowsOfPage= 15

                SELECT pestoque.NomeEstoque,pmarca.Marca
                ,pbasico.[SKU],pbasico.[NomeProduto]
                ,pbasico.[SaldoAtual],
                CASE
                    WHEN pbasico.BitAtivo = 1 THEN 'ProdutoAtivo'
                    WHEN pbasico.BitAtivo = 0 THEN 'ProdutoInativo'
                    ELSE 'NaoAvaliado'
                END 'STATUSPRODUTO',
                CASE
                    WHEN pbasico.[bitLinha] = 0 THEN  'ForaDeLinha'
                    WHEN pbasico.[bitLinha] = 1 THEN  'EmLinha'
                    ELSE 'NaoAvaliado'
                END 'STATUSPRODUTOLINHA',
                CASE
                    WHEN pestoque.NomeEstoque = 'Fisico' THEN 'Disponivel'
                    ELSE 'CrossDocking'
                END 'STATUSESTOQUE'
                FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico
                JOIN [HauszMapa].[Produtos].[Marca] as pmarca
                ON pmarca.IdMarca = pbasico.IdMarca
                JOIN [HauszMapa].[Estoque].[Estoque] as pestoque
                ON pestoque.IdEstoque = pbasico.EstoqueAtual
                where pestoque.NomeEstoque in ('Fisico')

                ORDER BY pbasico.[SaldoAtual] DESC
                OFFSET (@PageNumber-1)*@RowsOfPage ROWS
                FETCH NEXT @RowsOfPage ROWS ONLY
               """.format(page)))

            saldos_estoques = conn.execute(exec).all()
            for saldos in saldos_estoques:
                dict_items = {
                    'Marca': saldos[1],
                    'SKU': saldos[2],
                    'NOMEPRODUTO': saldos[3],
                    'ESTOQUE': saldos[0],
                    'SALDOPRODUTO': round(saldos[4], 2),
                    'STATUSPRODUTO': saldos[5],
                    'PRODUTOLINHA': saldos[6],
                    'STATUSESTOQUE': saldos[7]}

                lista_dicts.append(dict_items)

        return self.render('admin/saldodisponivel.html', page=page, produtos=lista_dicts, filtro_marcas=marcas, estoque=estoques)

    @expose('/prazosprodutosmarcas/<int:page>', methods=('GET', 'POST'))
    def prazos_view(self, page=1):

        lista_dict_marcas = []
        with db.engine.connect() as conn:
            exec = (text("""DECLARE @PageNumber AS INT
                      DECLARE @RowsOfPage AS INT
                      SET @PageNumber= {}
                      SET @RowsOfPage= 15
                      SELECT  distinct pmarca.Marca
                      ,cast(saldos.[DataAtualizado] as date) as 'ultimaatualizacao'
                      ,saldos.[IdMarca],
                      CASE
                          WHEN pmarca.BitAtivo = 1 THEN 'Marca Ativa'
                          WHEN pmarca.BitAtivo = 0 THEN 'Marca Inativa'
                      ELSE 'Nao Foi Possivel Verificar'
                      END 'StatusMarca'
                      FROM [HauszMapa].[Produtos].[ProdutosSaldos] as saldos
                      join [HauszMapa].[Produtos].[Marca] as pmarca
                      on pmarca.IdMarca = saldos.IdMarca
                      join Produtos.ProdutoBasico as pbasico
                      on pbasico.SKU = saldos.SKU
                      group by pmarca.Marca,cast(saldos.[DataAtualizado] as date)
                      ,saldos.[IdMarca],pmarca.BitAtivo
                      order by ultimaatualizacao desc 
                      OFFSET (@PageNumber-1)*@RowsOfPage ROWS
                      FETCH NEXT @RowsOfPage ROWS ONLY""".format(page)))
            exec_produtos = conn.execute(exec).all()

            for marcas in exec_produtos:
                lista_dict_marcas.append(marcas)

        return self.render('admin/prazosprodutos.html', page=page, produtos=lista_dict_marcas)

    @expose('/semcadastroprodutos', methods=('GET', 'POST'))
    def marcas_atualizadas_dia(self):
        lista_dicts = []
        marcas = select_marcas()
        with db.engine.connect() as conn:
            exec = (text("""SELECT pmarca.Marca ,COUNT(pbasico.[SKU]) AS 'QUANTIDADEPRODUTOS'

            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            WHERE  pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
            WHERE convert(VARCHAR, psaldo.DataAtualizado
            , 23) = CONVERT(date, GETDATE())  AND pbasico.BitAtivo = 1)
            GROUP BY pmarca.Marca"""))

            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_items = {
                    'MARCA': produto[0],
                    'SKUS': produto[1]


                }
                print(dict_items)
                lista_dicts.append(dict_items)
            cont = len(lista_dicts)

        return self.render('admin/semcadastro.html', produtos=lista_dicts, marcas_produtos=marcas)

    @expose("semcadastro/<marca>", methods=('GET', 'POST'))
    def retorna_diario_marca(self, marca):
        lista_dicts = []

        with db.engine.connect() as conn:
            exec = (text(""" 
            SELECT pmarca.Marca ,pbasico.[SKU] ,pbasico.[NomeProduto] 
            ,psaldo.Quantidade,
            pprazo.PrazoEstoqueFabrica,pprazo.PrazoFaturamento,pprazo.PrazoOperacional
            ,pprazo.PrazoProducao,pprazo.PrazoTotal,convert(VARCHAR, psaldo.DataAtualizado, 23) AS 'DATAATUALIZADO',
            CASE
                WHEN pbasico.[BitAtivo] = 1 THEN 'ProdutoAtivo'
                WHEN pbasico.[BitAtivo] = 0 THEN 'ProdutoInativo'

                ELSE 'NaoAvaliado'
            END 'StatusBitAtivo',

            CASE
                WHEN convert(VARCHAR, psaldo.DataAtualizado, 23) = CONVERT (date, GETDATE())  THEN 'MarcaAtualizado'
                WHEN  convert(VARCHAR, psaldo.DataAtualizado, 23) < CONVERT (date, GETDATE()) THEN 'MarcaNaoAtualizada'
                ELSE 'NaoAvaliado'
            END 'StatusAtualizado'

            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            JOIN [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pprazo
            ON pprazo.SKU = pbasico.SKU
            WHERE   pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
            WHERE convert(VARCHAR, psaldo.DataAtualizado
            , 23) = CONVERT(date, GETDATE())  AND pbasico.BitAtivo = 1 and pmarca.Marca in ('{}'))
                """.format(marca)))

            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_items = {
                    'MARCA': produto[0],
                    'NomeProduto': produto[2],
                    'SKU': produto[1],
                    'Quantidade': round(produto[3], 2),
                    'PrazoEstoqueFabrica': produto[4],
                    'PrazoFaturamento': produto[5],
                    'PrazoOperacional': produto[6],
                    'PrazoProducao': produto[7],
                    'PrazoTotal': produto[8],
                    'dataatualizacao': produto[9]
                }
                print(dict_items)
                lista_dicts.append(dict_items)
            print(len(lista_dicts))
        return self.render('admin/detalheatualizados.html', produtos=lista_dicts)

    @expose('/naoatualizados', methods=('GET', 'POST'))
    def nao_atualizados(self):
        lista_marcas = select_marcas()
        lista_dicts = []
        somados = []
        with db.engine.connect() as conn:
            exec = (text(""" 
            SELECT pmarca.Marca ,COUNT(pbasico.[SKU]) AS 'QUANTIDADEPRODUTOS'
            ,convert(VARCHAR, psaldo.DataAtualizado, 23) as 'dataultimaatualizacao'

            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            WHERE  pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
            WHERE convert(VARCHAR, psaldo.DataAtualizado
            , 23) <= CONVERT(DATE, DATEADD(DAY, -1, GETDATE())) AND pbasico.BitAtivo = 1)
            GROUP BY pmarca.Marca,convert(VARCHAR, psaldo.DataAtualizado, 23)
                            """))

            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_items = {
                    'MARCA': produto[0],
                    'SKUS': int(produto[1]),
                    'dataultimaatualizacao': produto[2]



                }

                somados.append(produto[1])

                lista_dicts.append(dict_items)

        print(somados)

        return self.render('admin/produtoatualizado.html', produtos=lista_dicts, marcas=lista_marcas)

    @expose('/detalhanaoatualizados/<marca>', methods=('GET', 'POST'))
    def detalhapormarca(self, marca):
        lista_dicts = []
        with db.engine.connect() as conn:

            exec = (text("""
            SELECT pmarca.Marca ,pbasico.[SKU] ,pbasico.[NomeProduto] 
            ,psaldo.Quantidade,
            pprazo.PrazoEstoqueFabrica,pprazo.PrazoFaturamento,pprazo.PrazoOperacional
            ,pprazo.PrazoProducao,pprazo.PrazoTotal,convert(VARCHAR, psaldo.DataAtualizado, 23) AS 'DATAATUALIZADO',
            CASE
                WHEN pbasico.[BitAtivo] = 1 THEN 'ProdutoAtivo'
                WHEN pbasico.[BitAtivo] = 0 THEN 'ProdutoInativo'

                ELSE 'NaoAvaliado'
            END 'StatusBitAtivo',

            CASE
                WHEN convert(VARCHAR, psaldo.DataAtualizado, 23) = convert(VARCHAR, GETDATE(), 23) THEN 'MarcaAtualizado'
                WHEN  convert(VARCHAR, psaldo.DataAtualizado, 23) < convert(VARCHAR, GETDATE(), 23) THEN 'MarcaNaoAtualizada'
                ELSE 'NaoAvaliado'
            END 'StatusAtualizado'

            FROM [HauszMapa].[Produtos].[ProdutoBasico] AS pbasico
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            JOIN [HauszMapa].[Produtos].[ProdutosSaldos] AS psaldo
            ON psaldo.SKU = pbasico.SKU
            JOIN [HauszMapa].[Produtos].[ProdutoPrazoProducFornec] as pprazo
            ON pprazo.SKU = pbasico.SKU
            WHERE   pbasico.SKU IN (SELECT DISTINCT SKU FROM [HauszMapa].[Produtos].[ProdutosSaldos]
            WHERE convert(VARCHAR, psaldo.DataAtualizado
            , 23) = convert(date, DATEADD(DAY, -1,getdate())) AND pbasico.BitAtivo = 1 and pmarca.Marca in ('{}'))
                            """.format(marca)))

            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_items = {
                    'MARCA': produto[0],
                    'NomeProduto': produto[1],
                    'SKU': produto[2],
                    'Quantidade': produto[3],
                    'PrazoEstoqueFabrica': produto[4],
                    'PrazoFaturamento': produto[5],
                    'PrazoOperacional': produto[6],
                    'PrazoProducao': produto[7],
                    'PrazoTotal': produto[8],
                    'dataatualizacao': produto[9]
                }

                lista_dicts.append(dict_items)

        return self.render('admin/detalhanaoatualizado.html', produtos=lista_dicts)

    @expose('/referenciamarca', methods=('GET', 'POST'))
    def referencia_marcas(self):
        lista_produtos = []
        marca = select_marcas()
        status_marca = ['MarcaAtiva', 'MarcaInativa']
        with db.engine.connect() as conn:
            exec = (text("""
          
                SELECT pmarca.Marca,pmarca.IdMarca
                ,count(pbasico.[SKU]) as 'totalprodutos',pmarca.BitAtivo,
                CASE
                    WHEN pmarca.BitAtivo = 1 THEN 'MarcaAtiva'
                    WHEN pmarca.BitAtivo = 0 THEN 'MarcaInativa'
                    ELSE 'Naoavaliado'
                END 'StatusMarca'
                FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico 
                JOIN [HauszMapa].[Produtos].[Marca] as pmarca
                ON pmarca.IdMarca = pbasico.IdMarca
                GROUP BY  pmarca.Marca,pmarca.IdMarca,pmarca.BitAtivo
                """))
            exec_produtos = conn.execute(exec).all()
            for produto in exec_produtos:
                dict_item = {
                    'MARCA': produto[0],
                    'IDMARCA': produto[1],
                    'TOTALSKUS': produto[2],
                    'STATUS': produto[3],
                }
                print(dict_item)
                lista_produtos.append(dict_item)

        return self.render('admin/referenciamarcas.html', produtos=lista_produtos, marcas_produtos=marca, status=status_marca)

    @expose('/referenciamarca/<marca>', methods=('GET', 'POST'))
    def detalha_marca_produto(self, marca):
        lista_produtos = []
        with db.engine.connect() as conn:
            exec = (text("""
        
            SELECT pmarca.Marca,pmarca.IdMarca,pbasico.[SKU] ,pbasico.[NomeProduto]
            FROM [HauszMapa].[Produtos].[ProdutoBasico] as pbasico  
            JOIN [HauszMapa].[Produtos].[Marca] as pmarca
            ON pmarca.IdMarca = pbasico.IdMarca
            WHERE pmarca.Marca = '{}'
            """.format(marca)))
            exec_produtos = conn.execute(exec).all()

            for produto in exec_produtos:

                dict_item = {
                    'MARCA': produto[0],
                    'IDMARCA': produto[1],
                    'SKU': produto[2],
                    'NOME': produto[3],
                }
                print(dict_item)

                lista_produtos.append(dict_item)

        return self.render('admin/marcadetalhe.html', produtos=lista_produtos)


class ArquivosConvertidosView(ModelView):
    page_size = 20

    create_modal = True
    # column_exclude_list = ['password_hash']
    column_display_pk = True
    column_searchable_list = ['SKU']
    can_view_details = True
    column_list = ['SKU', 'idarquivo',
                   'saldoproduto', 'dataatualizado', 'marca']

    column_filters = [

        'SKU', 'marca', 'dataatualizado'

    ]
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True


class UserView(ModelView):
    can_set_page_size = True
    page_size = 15
    create_modal = True
    column_sortable_list = ('IdProduto', ('IdProduto', Usuarios.id_usuario))
    column_display_pk = True
    column_searchable_list = [
        'nome', 'email', 'datalogado', 'datacadastro', 'status_login', 'grupo']
    can_view_details = True
    column_list = ['id_usuario', 'id_grupo', 'nome',
                   'email', 'bitusuario', 'status_login', 'grupo']
    # column_default_sort = ('last_name', False)
    column_filters = ['nome', 'email', 'grupo', 'status_login', 'datalogado']
    column_sortable_list = ('id_usuario',)
    column_default_sort = 'id_usuario'


class ProdutoPrazoProducFornecView(ModelView):
    can_set_page_size = True
    page_size = 15
    create_modal = True
    column_sortable_list = (
        'IdPrazos', ('IdPrazos', ProdutoPrazoProducFornec.IdPrazos))
    column_display_pk = True
    column_searchable_list = ['SKU']
    column_list = ['SKU', 'PrazoEstoqueFabrica', 'PrazoProducao',
                   'PrazoOperacional', 'PrazoFaturamento', 'PrazoTotal']
    column_filters = ['SKU']
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True
    column_sortable_list = ('IdPrazos',)
    column_default_sort = 'IdPrazos'
    column_details_list = ['PrazoProducao']
    column_filters = ['SKU']


class Deparaview(ModelView):
    can_set_page_size = True
    page_size = 15
    create_modal = True
    column_sortable_list = (
        'IdProduto', ('IdProduto', DeparaProdutos.iddepara))
    column_display_pk = True
    column_searchable_list = [
        'marca', 'statusdepara', 'referenciahausz', 'nomeproduto']
    can_view_details = True
    column_list = ['iddepara', 'IdProduto', 'ean', 'statusdepara',
                   'referenciafabricante', 'referenciahausz', 'nomeproduto', 'idmarcahausz', 'marca', 'bitativo']
    # column_default_sort = ('last_name', False)
    column_filters = [

        'marca', 'statusdepara', 'referenciahausz', 'nomeproduto'

    ]
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True
    column_sortable_list = ('iddepara',)
    column_default_sort = 'iddepara'


class ProdutosSaldosView(ModelView):
    can_set_page_size = True
    page_size = 15
    column_display_pk = True
    create_modal = True
    column_sortable_list = (
        'IdProdutosSaldos', ('IdProdutosSaldos', ProdutosSaldos.IdProdutosSaldos))
    column_searchable_list = ['SKU', 'IdMarca', 'DataAtualizado']
    can_view_details = True
    column_list = ['SKU', 'IdMarca', 'Quantidade', 'DataAtualizado']
    # column_default_sort = ('last_name', False)
    column_filters = [

        'SKU', 'Quantidade', 'DataAtualizado'

    ]
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True
    column_display_all_relations = True
    column_sortable_list = ('IdProdutosSaldos',)
    column_default_sort = 'IdProdutosSaldos'


class ColetadosView(ModelView):
    create_modal = True
    column_display_pk = True
    column_searchable_list = ['referenciahausz', 'referenciafabricante',
                              'nomeproduto', 'saldo', 'BitAtivo', 'dataalteracao']
    can_view_details = True
    column_list = ['referenciahausz', 'referenciafabricante', 'nomeproduto',
                   'CodBarras', 'saldo', 'prazo', 'BitAtivo', 'alteradopor', 'dataalteracao']
    # column_default_sort = ('last_name', False)
    column_filters = [

        'referenciahausz', 'referenciafabricante', 'nomeproduto', 'BitAtivo',

    ]
    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True


class SellersPricesView(ModelView):
    can_set_page_size = True
    page_size = 15
    column_display_pk = True
    create_modal = True
    column_sortable_list = (
        'IdSeller', ('IdSeller', SellersPrices.IdSeller))
    column_searchable_list = ['skuhausz', 'idprodutohausz', 'marcaprodutoseller','idmarcahausz'
    ,'eanreferebcia','nomeseller','nomeproduto']
    can_view_details = True
    column_list = ['paginaprodutoseller','paginaprodutogoogle','skuhausz', 'idprodutohausz', 'nomeproduto',
    'nomeseller','precoprodutoseller','metroseller','marcaprodutoseller','precohausz','diferenciapreco','dataatualizado']
    # column_default_sort = ('last_name', False)
    column_filters = [

        'skuhausz', 'marcaprodutoseller', 'nomeproduto','nomeseller'

    ]

    can_create = True
    can_edit = True
    Can_delete = True
    can_export = True
    column_display_all_relations = True
    column_sortable_list = ('IdSeller',)
    column_default_sort = 'IdSeller'



class IndesView(BaseView):
    @expose('/')
    def Home(self):

        produtos_crossdocking = DashAdmin(1).resumo_produtos(1)
        cont_natualizado = DashAdmin(1).cont_produtos(1)

        produtos_disponivel = DashAdmin(0).resumo_produtos(0)
        cont_estoque = DashAdmin(0).produto_estoque()
        cont_dia_nao_atualizado = DashAdmin().cont_produtos_nao_atualizado()

        return self.render('admin/index.html', produtosc=produtos_crossdocking, cont_natualizado=cont_natualizado, produtoe=produtos_disponivel, cont_estoque=cont_estoque, nao_tot=cont_dia_nao_atualizado)


path = os.path.join(UPLOADFOLDER, 'flaskapprefatorado',
                    'app', 'admin', 'files', 'adminuploads')


admin.add_view(NotificationsView(name='Notifications', endpoint='notify'))


admin.add_view(ProdutoPrazoProducFornecView(
    ProdutoPrazoProducFornec, db.session, category="Produtos"))
admin.add_view(ProdutosSaldosView(
    ProdutosSaldos, db.session, category="Produtos"))
admin.add_view(Deparaview(DeparaProdutos, db.session, category="Produtos"))

admin.add_view(ArquivosConvertidosView(
    ArquivosConvertidos, db.session, category="Produtos"))
admin.add_view(ModelView(ColetadosDiario, db.session, category="Produtos"))
admin.add_view(SellersPricesView(SellersPrices,db.session, category="Produtos"))
admin.add_sub_category(name="Links", parent_name="Produtos")

admin.add_view(UserView(Usuarios, db.session))

admin.add_link(MenuLink(name='Dashboard', url='/'))


admin.add_view(FileAdmin(path, '/adminuploads/',
               name='AnexarArquivos', category="AtualizacaoProdutos"))


admin.add_sub_category(name="AtualizacaoProdutos",
                       parent_name="AtualizacaoProdutos")


admin.add_link(MenuLink(name="MonitoramentoDePrecos",
               url="/monitoramentodeprecos/1"))
admin.add_link(MenuLink(name='Sair', url='/logout', category="Acessos"))
admin.add_link(MenuLink(name='Login', url='/login', category="Acessos"))
admin.add_sub_category(name="Acessos", parent_name="Acessos")


@adm.route('/adminuploads/<name>')
def download_files_admin(name):

    path = os.path.join(UPLOADFOLDER, 'flaskapprefatorado',
                        'app', 'admin', 'files', 'adminuploads')
    filename = os.path.join(path, name)

    return send_from_directory(path, name)
