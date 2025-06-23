// Login Function
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const db = document.getElementById('db').value;
  const login = document.getElementById('login').value;
  const password = document.getElementById('password').value;
  const errorMessage = document.getElementById('errorMessage');
  
  try {
    console.log("Sending login request with:", { db, login, password });

    const response = await fetch('http://localhost:8069/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        method: "call",
        params: {
          db: db,
          login: login,
          password: password
        }
      })
    });

    const data = await response.json();
    console.log("Login success data:", data);

    const result = data.result;

    if (!result || result.status !== "success") {
      throw new Error(result?.message || 'Login failed');
    }

    const token = result.token;

    if (token) {
      localStorage.setItem('token', token);
      window.location.href = 'dashboard.html';
    } else {
      throw new Error('No token received');
    }
  } catch (error) {
    console.error("Full error details:", error);
    errorMessage.textContent = error.message || 'Login failed. Check console for details.';
    errorMessage.classList.remove('d-none');
  }
});


// Logout Function
document.getElementById('logoutBtn')?.addEventListener('click', async () => {
  const token = localStorage.getItem('token');
  
  try {
    await fetch('http://localhost:8069/api/auth/logout', {
      method: 'POST',
      headers: { 'Authorization': token }
    });
    
    localStorage.removeItem('token');
    window.location.href = 'index.html';
  } catch (error) {
    console.error('Logout error:', error);
  }
});

// Protect routes
if (window.location.pathname.includes('dashboard.html') || 
    window.location.pathname.includes('update_task.html')) {
  if (!localStorage.getItem('token')) {
    window.location.href = 'index.html';
  }
}