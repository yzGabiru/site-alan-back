from flask import Flask, jsonify, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)

# Substitua com sua string de conexão
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://zgabiru:123456@localhost:5432/atividade_alan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '2f2be5642b7f927769811a0efbca650d'  # Troque por uma chave forte em produção

db = SQLAlchemy(app)
CORS(app, supports_credentials=True)

# Modelo de usuário
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(300), nullable=False)

# Middleware de autenticação
def login_requerido(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return jsonify({'error': 'Acesso não autorizado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# Rota inicial
@app.route('/')
def index():
    return "API Funcionando!"

# Listar usuários (requer login)
@app.route('/usuarios')
@login_requerido
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([
        {'id': u.id, 'nome': u.nome, 'email': u.email}
        for u in usuarios
    ])

# Registrar novo usuário
@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    dados = request.get_json()
    nome = dados.get('nome')
    email = dados.get('email')
    senha = dados.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Dados incompletos'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    senha_hash = generate_password_hash(senha)
    novo_usuario = Usuario(nome=nome, email=email, senha=senha_hash)
    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'message': 'Usuário registrado com sucesso!'}), 201

# Login
@app.route('/login', methods=['POST'])
def login_usuario():
    dados = request.get_json()
    email = dados.get('email')
    senha = dados.get('senha')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not check_password_hash(usuario.senha, senha):
        return jsonify({'error': 'Credenciais inválidas'}), 401

    session['usuario_id'] = usuario.id
    return jsonify({'message': 'Login realizado com sucesso!'})

# Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('usuario_id', None)
    return jsonify({'message': 'Logout realizado com sucesso!'})

if __name__ == '__main__':
    app.run(debug=True)
