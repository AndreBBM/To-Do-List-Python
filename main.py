from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
from datetime import datetime
from werkzeug.exceptions import BadRequest
import json

# Inicializando o aplicativo Flask e as extensões
app = Flask(__name__)

# Configuração do banco de dados MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:0909@localhost/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializando o banco de dados SQLAlchemy
db = SQLAlchemy(app)

# Inicializando o Redis
redis = Redis(host='localhost', port=6379, db=0)

# Modelo de Tarefa
class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Função para validar dados da tarefa
def validate_task_data(data):
    if 'title' not in data or not data['title']:
        raise BadRequest("O título da tarefa não pode ser vazio.")
    return data

# Endpoint para adicionar uma nova tarefa
@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()

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
        return jsonify({"tasks": json.loads(cached_tasks)}), 200

    # Se não estiver no cache, pegar do banco de dados
    tasks = Task.query.all()
    tasks_list = [{"id": task.id, "title": task.title, "status": task.status} for task in tasks]

    # Salvar no cache para o futuro
    redis.set('all_tasks', json.dumps(tasks_list))

    return jsonify({"tasks": tasks_list}), 200


@app.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Tarefa não encontrada"}), 404
    
    # Atualizando a tarefa
    task.title = request.json['title']
    task.status = request.json['status']
    db.session.commit()

    # Invalidar o cache após a atualização
    redis.delete('all_tasks')

    return jsonify({"message": "Tarefa atualizada com sucesso"}), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return jsonify({"message": "Tarefa não encontrada"}), 404

    # Deletando a tarefa
    db.session.delete(task)
    db.session.commit()

    # Invalidar o cache após a exclusão
    redis.delete('all_tasks')

    return jsonify({"message": "Tarefa deletada com sucesso"}), 200

# Rota para verificar se a API está funcionando
@app.route('/')
def index():
    return jsonify({"message": "API de To-Do List funcionando!"}), 200

# Função para inicializar o banco de dados e o cache
def init_db():
    db.create_all()

# Inicializar o banco de dados (caso as tabelas não existam)
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(debug=True)
