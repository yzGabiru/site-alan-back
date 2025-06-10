import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'troque_isto')
db = SQLAlchemy(app)
CORS(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(300), nullable=False)
    pontos = db.Column(db.Integer, default=0)

class Premio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    custo = db.Column(db.Integer, nullable=False)

jwt = JWTManager(app)

@app.route('/')
def index():
    return "API Funcionando!"

@app.route('/registrar', methods=['POST'])
def registrar():
    dados = request.get_json()
    if not all(k in dados for k in ('nome','email','senha')):
        return jsonify({'erro':'Dados incompletos'}), 400
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'erro':'Email já cadastrado'}), 400
    usr = Usuario(
        nome=dados['nome'],
        email=dados['email'],
        senha=generate_password_hash(dados['senha']),
        pontos=100  # pontos iniciais (exemplo)
    )
    db.session.add(usr)
    db.session.commit()
    return jsonify({'message':'Registrado com sucesso!'}),201

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    usr = Usuario.query.filter_by(email=dados.get('email')).first()
    if not usr or not check_password_hash(usr.senha, dados.get('senha','')):
        return jsonify({'erro':'Credenciais inválidas'}),401
    token = create_access_token(identity=usr.id)
    return jsonify({'access_token':token}),200

@app.route('/usuario/pontos', methods=['GET'])
@jwt_required()
def meus_pontos():
    uid = get_jwt_identity()
    usr = Usuario.query.get(uid)
    return jsonify({'pontos': usr.pontos})

@app.route('/premios', methods=['GET'])
@jwt_required()
def listar_premios():
    lst = Premio.query.all()
    return jsonify([{'id':p.id,'nome':p.nome,'custo':p.custo} for p in lst])

@app.route('/resgatar', methods=['POST'])
@jwt_required()
def resgatar():
    uid = get_jwt_identity()
    dados = request.get_json()
    premio = Premio.query.get(dados.get('premio_id'))
    usr = Usuario.query.get(uid)
    if not premio:
        return jsonify({'erro':'Prêmio não existe'}),404
    if usr.pontos < premio.custo:
        return jsonify({'erro':'Pontos insuficientes'}),400
    usr.pontos -= premio.custo
    db.session.commit()
    return jsonify({'message':'Resgate efetuado','pontos_restantes':usr.pontos})

if __name__=='__main__':
    app.run(debug=True)