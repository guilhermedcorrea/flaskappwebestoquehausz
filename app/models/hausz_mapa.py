from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,BooleanField,DateField
from wtforms.validators import InputRequired, Length,DataRequired
from werkzeug.security import check_password_hash, generate_password_hash
from flask_admin.contrib.sqla.ajax import QueryAjaxModelLoader

db = SQLAlchemy()
def configure(app):
    db.init_app(app)
    app.db = db


class ProdutosSaldos(db.Model):
    __tablename__ = "ProdutosSaldos"
    __table_args__ = {"schema": "Produtos"}
    IdProdutosSaldos = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(1000), unique=False, nullable=False)
    IdMarca = db.Column(db.Integer)
    Quantidade = db.Column(db.Float)
    DataAtualizado = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return f'{self.IdProdutosSaldos},{self.SKU},{self.IdMarca},{self.Quantidade},{self.DataAtualizado}'


class SellersPrices(db.Model):
    _tablename_ = "SellersPrices"
    IdSeller = db.Column(db.Integer, primary_key=True)
    paginaprodutoseller = db.Column(db.String, unique=False, nullable=False)
    paginaprodutogoogle = db.Column(db.String, unique=False, nullable=False)
    idgoogleshopping = db.Column(db.Integer)
    nomeproduto = db.Column(db.String, unique=False, nullable=False)
    nomeseller = db.Column(db.String, unique=False, nullable=False)
    eanreferebcia = db.Column(db.String, unique=False, nullable=False)
    precoprodutoseller  = db.Column(db.Float)
    metroseller  = db.Column(db.Float)
    urlimagemproduto = db.Column(db.String, unique=False, nullable=False)
    marcaprodutoseller = db.Column(db.String, unique=False, nullable=False)
    categoriaprodutoseller = db.Column(db.String, unique=False, nullable=False)
    idmarcahausz = db.Column(db.Integer)
    urlcategoriaprodutoseller = db.Column(db.String, unique=False, nullable=False)
    categoriahausz = db.Column(db.String, unique=False, nullable=False)
    idprodutohausz = db.Column(db.Integer)
    skuhausz = db.Column(db.String, unique=False, nullable=False)
    precohausz  = db.Column(db.Float)
    diferenciapreco = db.Column(db.Integer)
    dataatualizado = db.Column(db.DateTime, unique=False, nullable=False)


class Usuarios(db.Model, UserMixin):
    __tablename__ = 'Users'
    __bind_key__ = 'HauszMapaDev2'
    id_usuario = db.Column(db.Integer, primary_key=True)
    id_grupo = db.Column(db.Integer)
    nome = db.Column(db.String(100), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(900), unique=False, nullable=False)
    bitusuario = db.Column(db.Boolean, nullable=False)
    bitlogado = db.Column(db.Boolean, nullable=False)
    datalogado = db.Column(db.DateTime, unique=False, nullable=False)
    datacadastro = db.Column(db.DateTime, unique=False, nullable=False)
    status_login = db.Column(db.String(30), unique=False, nullable=False)
    grupo = db.Column(db.String(100), unique=False, nullable=False)

    def __init__(self, email, nome, password):
        self.email = email
        self.nome = nome
        self.password_hash = password

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    # Custom property setter
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_active(self):
        return True

    def get_id(self):
        return self.id_usuario

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__(self):
        return f"User('{self.nome}', '{self.email}', '{self.id_usuario}')"





class LoginForm(FlaskForm):
    Usuario = StringField('Usuario', validators=[InputRequired(), Length(min=4, max=15)])
    Senha = PasswordField('Senha', validators=[InputRequired(), Length(min=2, max=80)])

    remember = BooleanField('Remember me')


class GrupoUsuario(db.Model):
    __tablename__ = 'UsersGroup'
    __bind_key__ = 'HauszMapaDev2'
    id_grupo = db.Column(db.Integer, primary_key=True)
    nome_grupo = db.Column(db.String(200), unique=False, nullable=False)
    bitativo = db.Column(db.Boolean, nullable=False)
    datacadastro = db.Column(db.DateTime, unique=False, nullable=False)

    def __repr__(self):
        return f'{self.nome_grupo}'




class ProdutoPrazoProducFornec(db.Model):
    __tablename__ = "ProdutoPrazoProducFornec"
    __table_args__ = {"schema": "Produtos"}
    IdPrazos = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(1000), unique=False, nullable=False)
    PrazoEstoqueFabrica = db.Column(db.Float)
    PrazoProducao = db.Column(db.Float)
    PrazoOperacional = db.Column(db.Float)
    PrazoFaturamento = db.Column(db.Float)
    PrazoTotal = db.Column(db.Float)
   


    def __repr__(self):
        return f'{self.SKU}'




class ProdutoBasico:
    __tablename__ = 'ProdutoBasico'
    __table_args__ = {"schema": "Produtos"}
    IdProduto = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(100), unique=False, nullable=False)
    CodOmie = db.Column(db.Integer)
    NomeProduto = db.Column(db.String(250), unique=False, nullable=False)
    NomeEtiqueta = db.Column(db.String(200), unique=False, nullable=False)
    NomeTotem = db.Column(db.String(200), unique=False, nullable=False)
    EAN = db.Column(db.String(50), unique=False, nullable=False)
    NCM = db.Column(db.String(12), unique=False, nullable=False)
    CEST = db.Column(db.String(10), unique=False, nullable=False)
    DataInserido = db.Column(db.DateTime, unique=False, nullable=False)
    IdMarca = db.Column(db.Integer, ForeignKey('Marca.IdMarca'))
    ValorMinimo = db.Column(db.Float)
    bitLinha = db.Column(db.Boolean, nullable=False)
    BitAtivo = db.Column(db.Boolean, nullable=False)
    IdSubCat = db.Column(db.Integer)
    bitOmie = db.Column(db.Boolean, nullable=False)
    EstoqueAtual = db.Column(db.Integer)
    SaldoAtual = db.Column(db.Float)
    InseridoPor = db.Column(db.String(50), unique=False, nullable=False)
    DataAlteracao = db.Column(db.DateTime, unique=False, nullable=False)
    bitPromocao = db.Column(db.Boolean, nullable=False)
    bitOutlet = db.Column(db.Boolean, nullable=False)
    bitAmostra = db.Column(db.Boolean, nullable=False)
    bitAtualizadoPreco = db.Column(db.Boolean, nullable=False)
    bitPrecoAtualizado = db.Column(db.Boolean, nullable=False)
    PesoCubado = db.Column(db.Float)
    Peso = db.Column(db.Float)
    IdDept = db.Column(db.Integer)
    EstoqueLocal = db.Column(db.Integer)
    bitEasy = db.Column(db.Boolean, nullable=False)
    bitCadastradoJet = db.Column(db.Boolean, nullable=False)
    bitAtualizadoJet = db.Column(db.Boolean, nullable=False)
    OrdemPromocao = db.Column(db.Integer)
    UltimaAlteracao = db.Column(db.DateTime, unique=False, nullable=False)
 

    def __repr__(self):
        return f'{self.NomeProduto},{self.SKU}'



class ProdutoDetalhe:
    __tablename__ = 'ProdutoDetalhe'
    IdProduto = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(100), unique=False, nullable=False)
    IdMarca = db.Column(db.Integer)
    IdSubCat = db.Column(db.Integer)
    Descricao = db.Column(db.String(8000), unique=False, nullable=False)
    QuantidadeMinima = db.Column(db.Float)
    TamanhoBarra = db.Column(db.Float)
    Unidade = db.Column(db.String(2), unique=False, nullable=False)
    FatorVenda = db.Column(db.String(20), unique=False, nullable=False)
    FatorMultiplicador = db.Column(db.Float)
    FatorUnitario = db.Column(db.Float)
    UrlImagem = db.Column(db.String(5000), unique=False, nullable=False)
    Garantia = db.Column(db.Integer)
    Nimagem = db.Column(db.Integer)
    InseridoImagemJet = db.Column(db.Boolean, nullable=False)
    AtualizadoImagemJet = db.Column(db.Boolean, nullable=False)
    Comprimento = db.Column(db.Float)
    Largura = db.Column(db.Float)
    Altura = db.Column(db.Float)
    ValorMinimo = db.Column(db.Float)
    bitVerificadoFoto = db.Column(db.Boolean, nullable=False)
    Peso = db.Column(db.Float)
    bitAtivo = db.Column(db.Boolean, nullable=False)
    UsuarioAlteracao = db.Column(db.String(100), unique=False, nullable=False)
    DataInserido = db.Column(db.DateTime, unique=False, nullable=False)
    IdProdutoNaoUsaMais = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.SKU}'


class ProdutoMarca:
    __tablename__ = 'Marca'
    IdMarca = db.Column(db.Integer, primary_key=True)
    Marca = db.Column(db.String(150), unique=False, nullable=False)
    PrazoFabricacao = db.Column(db.Integer)
    PedidoMinimo = db.Column(db.Float)
    Sobre = db.Column(db.String(200), unique=False, nullable=False)
    Video = db.Column(db.String(250), unique=False, nullable=False)
    DataCadastro = db.Column(db.DateTime, unique=False, nullable=False)
    DataAtualizacao = db.Column(db.DateTime, unique=False, nullable=False)
    IncluidoPor = db.Column(db.String(150), unique=False, nullable=False)
    AlteradoPor = db.Column(db.String(150), unique=False, nullable=False)
    BitAtivo = db.Column(db.Boolean, nullable=False)
    IdMarca2 = db.Column(db.Integer)
    ImgNome = db.Column(db.String(200), unique=False, nullable=False)
    DiasAtualizacao = db.Column(db.Integer)
    bitShowRoom = db.Column(db.Boolean, nullable=False)
    IdMarcaJet = db.Column(db.Integer)

    def __repr__(self):
        return f'{self.Marca}'


class DeparaProdutos(db.Model):
    __tablename__ = 'DeparaProdutos'
    __bind_key__ = 'HauszMapaDev2'
    iddepara = db.Column(db.Integer, primary_key=True)
    IdProduto = db.Column(db.Integer)
    ean = db.Column(db.String(20))
    statusdepara = db.Column(db.String(30))
    referenciahausz = db.Column(db.String(200))
    nomeproduto = db.Column(db.String(500))
    referenciafabricante = db.Column(db.String(200))
    idmarcahausz = db.Column(db.Integer, nullable=True)
    marca = db.Column(db.String(200), nullable=True)
    alteradopor = db.Column(db.String(200), nullable=True)
    dataalterado = db.Column(db.DateTime, unique=False, nullable=False)
    bitativo = db.Column(db.Boolean, nullable=False)


class ColetadosDiario(db.Model):
    __tablename__ = 'ColetadosDiario'
    __bind_key__ = 'HauszMapaDev2'
    idcoletado = db.Column(db.Integer, primary_key=True)
    referenciahausz = db.Column(db.String(200), unique=False, nullable=False)
    referenciafabricante = db.Column(db.String(200), unique=False, nullable=False)
    CodBarras = db.Column(db.String(20), unique=False, nullable=True)
    nomeproduto = db.Column(db.String(500), unique=False, nullable=True)
    saldo = db.Column(db.Float, unique=False, nullable=True)
    prazo = db.Column(db.Integer, unique=False, nullable=True)
    BitAtivo = db.Column(db.Boolean, unique=False, nullable=True)
    dataalteracao = db.Column(db.DateTime, unique=False, nullable=True)
    alteradopor = db.Column(db.String(500), nullable=True)


class ArquivosConvertidos(db.Model):
    _tablename_='ArquivosConvertidos'
    __table_args__ = {"schema": "dbo"}
    idarquivo = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(200), unique=False, nullable=True)
    saldoproduto = db.Column(db.Float)
    IdMarca = db.Column(db.Integer)
    dataatualizado = db.Column(db.DateTime, unique=False, nullable=True)
    marca = db.Column(db.String(200), unique=False, nullable=True)


class LogAlteracoesEstoques(db.Model):
    _tablename_="LogAlteracoesEstoques"
    __bind_key__ = 'HauszMapaDev2'
    idlog = db.Column(db.Integer, primary_key=True)
    idusuario = db.Column(db.Integer)
    idprodutoalterado = db.Column(db.Integer)
    idmarcaalterada = db.Column(db.Integer)
    tipoalteracao = db.Column(db.String(200))
    valoranterior = db.Column(db.Float)
    valoralterado = db.Column(db.Float)
    dataalteracao = db.Column(db.DateTime, unique=False, nullable=True)

class TipoAlteracao(db.Model):
    _tablename_="TipoAlteracao"
    __bind_key__ = 'HauszMapaDev2'
    idtipo = db.Column(db.Integer, primary_key=True)
    alteracao = db.Column(db.String(200))
    bitativo = db.Column(db.Boolean, unique=False, nullable=True)