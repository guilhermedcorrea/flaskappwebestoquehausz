from flask import Blueprint
from flask import Flask, render_template, request, url_for, abort, \
    send_from_directory

import os
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template,current_app, jsonify, request, redirect, flash, url_for
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory


from config import UPLOADFOLDER


uploadestoques = Blueprint("uploadestoques",__name__,template_folder= "templates")


ALLOWED_EXTENSIONS = {'csv'}

current_app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),'excel_estoque')

from .query_estoques import ReaderExcelFile

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@uploadestoques.route('/uploadestoques', methods=['GET','POST'])
def upload_file_prazo():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploadestoques.download_file_prazo', name=filename))

    return render_template('upload_estoque.html')

@uploadestoques.route('/uploadestoques/<name>') 
#Recebe paramento com nome do arquivo e retorna json para o layout
def download_file_prazo(name):
    name = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER']))
    excelfile = ReaderExcelFile(name)
    excelfile.reader_file()

    dicts = excelfile.call_procedure_prazo_hausz_mapa()
    dicts = excelfile.call_procedure_saldo_hausz_mapa()
    produtos = excelfile.retorna_valores()
    print('printei', produtos)
 
   
    return render_template("tabela.html", produtos = produtos)

'''
@uploadestoques.route('/uploadestoques', methods=['GET','POST'])
def upload_prazo():
 
    files = os.listdir(os.path.join(current_app.config['UPLOAD_FOLDER']))
    excelfile = ReaderExcelFile(files)
    excelfile.reader_file()

    dicts = excelfile.call_procedure_prazo_hausz_mapa()
    dicts = excelfile.call_procedure_saldo_hausz_mapa()
    excelfile.retorna_valores()
  
    return render_template('upload_estoque.html', files=files)
 



@uploadestoques.route('/uploadestoques', methods=['GET','POST'])
def upload_file_estoques():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        if filename != '':
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in current_app.config['UPLOAD_EXTENSIONS']:
                
                return "Invalid image", 400
            uploaded_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
    

    return render_template('tabela.html')
   

@uploadestoques.route('/uploadestoques/<filename>')
def upload_prazos(filename):
    filesaldo = os.path.join(UPLOADFOLDER,'app','uploads','excel_estoque',filename)
    print(filename)
    excelfile = ReaderExcelFile(filesaldo)
    excelfile.reader_file()

    dicts = excelfile.call_procedure_prazo_hausz_mapa()
    dicts = excelfile.call_procedure_saldo_hausz_mapa()
   
    print(dicts)

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], filename)
    #return render_template('upload_estoque.html', produto=dicts)


'''