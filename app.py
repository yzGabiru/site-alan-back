import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime
app = Flask(__name__)

# 1) DATABASE: usa o ENV DATABASE_URL ou cai na sua string Postgres
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://postgres.ysrtgtczvjowdjvbakii:shineray3214@aws-0-sa-east-1.pooler.supabase.com:6543/postgres'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 2) JWT SECRET: pode sobrescrever com ENV JWT_SECRET_KEY
app.config['JWT_SECRET_KEY'] = os.getenv(
    'JWT_SECRET_KEY',
    'pKo7vYzZAK8Vb_gjwRWknT1cF-34UpQX'
)

db = SQLAlchemy(app)
CORS(app)
jwt = JWTManager(app)

# Modelos
class Usuario(db.Model):
    id     = db.Column(db.Integer, primary_key=True)
    nome   = db.Column(db.String(80), nullable=False)
    email  = db.Column(db.String(120), unique=True, nullable=False)
    senha  = db.Column(db.String(300), nullable=False)
    pontos = db.Column(db.Integer, default=0)

class Premio(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    nome  = db.Column(db.String(80), nullable=False)
    custo = db.Column(db.Integer, nullable=False)


class Resgate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    premio_id = db.Column(db.Integer, db.ForeignKey('premio.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='resgates')
    premio  = db.relationship('Premio')


# Rotas
@app.route('/')
def index():
    return "API Funcionando!"

@app.route('/registrar', methods=['POST'])
def registrar():
    d = request.get_json()
    if not all(k in d for k in ('nome','email','senha')):
        return jsonify({'erro':'Dados incompletos'}),400
    if Usuario.query.filter_by(email=d['email']).first():
        return jsonify({'erro':'Email já cadastrado'}),400
    u = Usuario(
        nome   = d['nome'],
        email  = d['email'],
        senha  = generate_password_hash(d['senha']),
        pontos = 100
    )
    db.session.add(u)
    db.session.commit()
    return jsonify({'message':'Registrado com sucesso!'}),201

@app.route('/login', methods=['POST'])
def login():
    d   = request.get_json()
    usr = Usuario.query.filter_by(email=d.get('email')).first()
    if not usr or not check_password_hash(usr.senha, d.get('senha','')):
        return jsonify({'erro':'Credenciais inválidas'}),401
    token = create_access_token(identity=usr.id)
    return jsonify({'access_token':token}),200

@app.route('/usuario/pontos', methods=['GET'])
@jwt_required()
def meus_pontos():
    uid = get_jwt_identity()
    usr = Usuario.query.get(uid)
    return jsonify({'pontos':usr.pontos})

@app.route('/premios', methods=['GET'])
@jwt_required()
def listar_premios():
    return jsonify([{'id':p.id,'nome':p.nome,'custo':p.custo}
                    for p in Premio.query.all()])

@app.route('/resgatar', methods=['POST'])
@jwt_required()
def resgatar():
    uid = get_jwt_identity()
    d = request.get_json()
    prem = Premio.query.get(d.get('premio_id'))
    usr = Usuario.query.get(uid)
    if not prem:
        return jsonify({'erro':'Prêmio não existe'}),404
    if usr.pontos < prem.custo:
        return jsonify({'erro':'Pontos insuficientes'}),400

    # debita pontos
    usr.pontos -= prem.custo
    # registra histórico
    r = Resgate(usuario_id=uid, premio_id=prem.id)
    db.session.add(r)
    db.session.commit()

    return jsonify({
        'message':'Resgate efetuado',
        'pontos_restantes':usr.pontos
    }),200

@app.route('/usuario/historico', methods=['GET'])
@jwt_required()
def historico():
    uid = get_jwt_identity()
    resgates = Resgate.query.filter_by(usuario_id=uid).order_by(Resgate.timestamp.desc()).all()
    result = []
    for r in resgates:
        result.append({
            'id': r.id,
            'nome': r.premio.nome,
            'custo': r.premio.custo,
            'data': r.timestamp.isoformat()
        })
    return jsonify(result),200

@app.route('/usuario/perfil', methods=['GET'])
@jwt_required()
def perfil():
    uid = get_jwt_identity()
    usr = Usuario.query.get(uid)
    return jsonify({
        'nome': usr.nome,
        'pontos': usr.pontos
    }), 200

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)