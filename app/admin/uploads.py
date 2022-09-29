from flask import (Blueprint, render_template
, request, redirect, url_for, abort, current_app)
from werkzeug.utils import secure_filename
import os
import flask_excel as excel


uploads = Blueprint("uploads", __name__)

from ..controllers.factory_classes import Produto


def register_handlers(app):
    if app.config.get('DEBUG') is True:
        app.logger.debug('Skipping error handlers in Debug mode')
        return

    @app.errorhandler(500)
    def server_error_page(*args, **kwargs):
        # retorna server error
        return render_template("teste_excecao.html"), 500

    @app.errorhandler(404)
    def TemplateNotFound(*args, **kwargs):
        # retorna template notfound
        return render_template("teste_excecao.html"), 404

    @app.errorhandler(404)
    def page_not_found(*args, **kwargs):
        # do stuff
        return render_template("teste_excecao.html"), 404
    
    @app.errorhandler(500)
    def ModuleNotFoundError(*args, **kwargs):
        return render_template("teste_excecao.html"), 500

    @app.errorhandler(403)
    def forbidden_page(*args, **kwargs):
        # do stuff
        return render_template("teste_excecao.html"), 403

    @app.errorhandler(404)
    def page_not_found(*args, **kwargs):
        # do stuff
        return render_template("teste_excecao.html"), 404

    @app.errorhandler(405)
    def method_not_allowed_page(*args, **kwargs):
        # do stuff
        return render_template("teste_excecao.html"), 405

register_handlers(current_app)

excel.init_excel(current_app)

@uploads.errorhandler(413)
def too_large(e):
    return "File is too large", 413


@uploads.route('/upload')
def upload_arquivos():
    files = os.listdir(current_app.config['UPLOAD_PATH'])
    print('aaaaaaaaaaaaaaaaaa',files)
    return render_template('upload.html', files=files)


@uploads.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']

    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:

            return "Invalid image", 400
        uploaded_file.save(os.path.join(current_app.config['UPLOAD_PATH'], filename))
        dicts = Produto(os.path.join(current_app.config['UPLOAD_PATH'], filename))
        dicts_products = dicts.retorna_marca()

        #print('aqui salvo',os.path.join(current_app.config['UPLOAD_PATH'], filename))
        return render_template("informacoesestoque.html", produtos=dicts_products)

    return '', 204


@uploads.route('/uploads/<filename>')
def upload(filename):
    filesaldo = (current_app.config['UPLOAD_PATH'], filename)

    dicts = Produto(filesaldo)

    dicts_products = dicts.retorna_marca()
    print(dicts_products)

    #return send_from_directory(current_app.config['UPLOAD_PATH'], filename)
    return render_template("informacoesestoque.html", produtos=dicts_products)


#export modelo planilhas


#Modelo arquivo alteração saldo fornecedor
@uploads.route("/modelosaldo", methods=['GET','POST'])
def export_modelo_alteracao_saldo():
    return excel.make_response_from_array([['SKU','MARCA','SALDO']],"xlsx",file_name="exportmodelosaldo.xlsx")

