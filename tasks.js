document.getElementById('createTaskForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const token = localStorage.getItem('token');
  if (!token) {
    alert('Please login first');
    window.location.href = 'index.html';
    return;
  }

  try {
    const submitBtn = document.querySelector('#createTaskForm button[type="submit"]');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
      <span class="spinner-border spinner-border-sm" role="status"></span>
      Creating...
    `;

    const taskData = {
      jsonrpc: "2.0",
      method: "call",
      params: {
        name: document.getElementById('taskName').value.trim(),
        project_id: parseInt(document.getElementById('projectId').value),
        stage_id: parseInt(document.getElementById('stageId').value),
        user_ids: document.getElementById('userIds').value.split(',').map(id => parseInt(id.trim())),
        description: document.getElementById('description').value.trim(),
        date_deadline: document.getElementById('deadline').value,
        company_id: 1
      }
    };

    console.log("Sending data:", JSON.stringify(taskData, null, 2));

    const response = await fetch('http://localhost:8069/api/task/create', {
      method: 'POST',
      headers: {
        'Authorization': token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(taskData)
    });

    const data = await response.json();
    console.log("Received response:", data);

    if (!response.ok || !data.result || data.error) {
      throw new Error(data?.error?.message || 'Unexpected server response');
    }

  } catch (error) {
    console.error('Error:', error);
    alert(`Error: ${error.message}`);
    
    if (error.message.includes('Unauthorized')) {
      localStorage.removeItem('token');
      window.location.href = 'index.html';
    }
  } finally {
    const submitBtn = document.querySelector('#createTaskForm button[type="submit"]');
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.innerHTML = 'Create Task';
    }
  }
});