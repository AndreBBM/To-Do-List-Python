document.getElementById("loginForm").addEventListener("submit", function(event) {
  event.preventDefault();

  const username = document.getElementById("username").value;
  const password = document.getElementById("password").value;

  fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
  })
  .then(response => response.json())
  .then(data => {
      if (data.access_token) {
          // Armazenar o token JWT no localStorage para futuras requisições
          localStorage.setItem("accessToken", data.access_token);
          document.getElementById("loginForm").style.display = "none";
          document.getElementById("loginTitle").style.display = "none";
          document.getElementById("taskContainer").style.display = "block";
          loadTasks();  // Função para carregar as tarefas
      } else {
          alert("Login failed");
      }
  })
  .catch(error => console.error("Error:", error));
});

function loadTasks() {
  const accessToken = localStorage.getItem("accessToken");

  fetch('http://127.0.0.1:5000/tasks', {
      method: 'GET',
      headers: {
          'Authorization': `Bearer ${accessToken}`
      }
  })
  .then(response => response.json())
  .then(data => {
      console.log("Tarefas:", data);
      // Exiba as tarefas na página HTML conforme desejado
  })
  .catch(error => console.error("Error:", error));
}


async function fetchTasks() {
  const response = await fetch('http://127.0.0.1:5000/tasks');
  const data = await response.json();
  const taskList = document.getElementById('task-list');
  taskList.innerHTML = '';  // Limpa a lista antes de exibir

  data.tasks.forEach(task => {
      const taskElement = document.createElement('div');
      taskElement.classList.add('task');
      taskElement.innerHTML = `
          <span>${task.title} - ${task.status}</span>
          <button onclick="updateTask(${task.id}, 'completa')">Mudar status</button>
          <button onclick="deleteTask(${task.id})">Remover</button>
      `;
      taskList.appendChild(taskElement);
  });
}

async function addTask() {
  const title = document.getElementById('new-task-title').value;
  if (!title) {
      alert('O título da tarefa não pode estar vazio.');
      return;
  }
  const accessToken = localStorage.getItem("accessToken");
  await fetch('http://127.0.0.1:5000/tasks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ title: title })
    })
    .then(response => response.json())
    .then(data => {
        console.log("Nova tarefa adicionada:", data);
        loadTasks();  // Atualizar a lista de tarefas
    })
    .catch(error => console.error("Error:", error));

  document.getElementById('new-task-title').value = '';
  fetchTasks();
}

async function updateTask(taskId, newStatus) {
  await fetch(`http://127.0.0.1:5000/tasks/${taskId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: newStatus })
  });
  fetchTasks();
}

async function deleteTask(taskId) {
  const accessToken = localStorage.getItem("accessToken");
  await fetch(`http://127.0.0.1:5000/tasks/${taskId}`, { method: 'DELETE',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${accessToken}`
    }})
    .then(response => response.json())
    .then(data => {
        console.log("Tarefa deletada:", data);
        loadTasks();  // Atualizar a lista de tarefas
    })
    .catch(error => console.error("Error:", error));

    document.getElementById('new-task-title').value = '';
    fetchTasks();
}

// Carregar as tarefas ao abrir a página
window.onload = fetchTasks;