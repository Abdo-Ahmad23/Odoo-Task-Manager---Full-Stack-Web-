A full-stack web application for managing tasks using Odoo as a backend and a responsive Bootstrap-based frontend.

🔐 Authentication System: Users can securely log in using their credentials via a custom API (/api/auth/login) with token-based authentication.

✅ Protected Routes: Only authenticated users can access the dashboard and create tasks.

🧠 Token Expiry Logic: Implements in-memory token storage with expiry validation for secure session handling.

📝 Task Creation: Authenticated users can create tasks via the API (/api/task/create) with required fields like task name, project, stage, and optional fields like assigned users, deadline, and description.

🚀 Frontend:

Built with HTML, CSS, and Vanilla JavaScript

UI styled using Bootstrap 5

Includes login page, task creation form, and protected routing

🌐 Backend:

Built using Odoo 15/16/18 (whichever version you're using)

Custom API endpoints written using Odoo HTTP controllers (@http.route)

CORS configured for frontend-backend interaction

📁 Tech Stack:
Frontend: HTML5, CSS3, JavaScript (ES6), Bootstrap 5

Backend: Odoo (Python)

API Protocol: JSON-RPC style

Auth: Token-based (stored in browser localStorage)![Screenshot from 2025-06-23 12-17-01](https://github.com/user-attachments/assets/0741bc41-be56-4613-a434-2d82253cbeea)
![Screenshot from 2025-06-23 12-16-46](https://github.com/user-attachments/assets/79c788eb-d02c-4cd9-88d2-4e71eeec41c8)
![Screenshot from 2025-06-23 12-15-51](https://github.com/user-attachments/assets/835a2739-38e9-4759-9c7b-6fcecdaf4087)


Dev Tools: Postman, VS Code, Git

