from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from datetime import datetime
from werkzeug.exceptions import BadRequest
import json
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
import bleach

with open("password.txt", "r") as file:
    senha_admin = file.read()

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "sua_chave_secreta"  # Use uma chave segura e privada
jwt = JWTManager(app)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:0909@localhost/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

redis = Redis(host='localhost', port=6379, db=0, decode_responses=True)

# Modelo de Tarefa
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Criar as tabelas, caso ainda não existam
with app.app_context():
    db.create_all()
    
# Função para validar dados da tarefa
def validate_task_data(data):
    if 'title' not in data or not data['title']:
        raise BadRequest("O título da tarefa não pode ser vazio.")
    return data

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if username == "admin" and password == senha_admin:
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"msg": "Usuário ou senha incorretos"}), 401
    

@app.route('/tasks', methods=['POST'])
@jwt_required()  # Garante que somente usuários autenticados podem acessar
def add_task():
    data = request.get_json()
    title = bleach.clean(data.get("title", ""))
    if not title:
        return jsonify({"error": "Título da tarefa não pode estar vazio."}), 400
    try:
        validate_task_data(data)
        task = Task(title=data['title'], status='pending')
        db.session.add(task)
        db.session.commit()

        # Atualizando o cache no Redis
        redis.set(f'task:{task.id}', str(task.id))

        return jsonify({"message": "Tarefa criada com sucesso!", "task": {"id": task.id, "title": task.title, "status": task.status}}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/tasks', methods=['GET'])
def get_tasks():

    redis.flushdb()
    # Verificar se os dados estão no cache
    cached_tasks = redis.get('all_tasks')
    if cached_tasks:
        return jsonify({"tasks": json.loads(cached_tasks)})
    
    tasks = Task.query.all()
    tasks_list = [{"id": task.id, "title": task.title, "status": task.status} for task in tasks]
    redis.set('all_tasks', json.dumps(tasks_list))
    return jsonify({"tasks": tasks_list})

@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Tarefa não encontrada"}), 404
    
    # se o status for "pending", muda para "done" e vice-versa
    task.status = "done" if task.status == "pending" else "pending"

    db.session.commit()

    redis.delete('all_tasks')

    return jsonify({"message": "Tarefa atualizada com sucesso"})

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Tarefa não encontrada"}), 404

    db.session.delete(task)
    db.session.commit()

    # Invalidar o cache após a exclusão
    redis.delete('all_tasks')

    return jsonify({"message": "Tarefa deletada com sucesso"}), 200

# Rota para verificar se a API está funcionando
@app.route('/')
def index():
    return jsonify({"message": "API de To-Do List funcionando!"}), 200

def init_db():
    db.create_all()

# Inicializar o banco de dados (caso as tabelas não existam)
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
