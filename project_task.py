import secrets
from datetime import datetime, timedelta
from odoo import http, _
from odoo.http import request
from odoo.exceptions import AccessDenied

TOKEN_MAP = {}
TOKEN_EXPIRY_HOURS = 24

class ProjectTaskAPI(http.Controller):

    # --- Helper Methods ---
    def _validate_token(self, token):
        """Check if token exists and is not expired."""
        if token not in TOKEN_MAP:
            return False
        if datetime.now() > TOKEN_MAP[token]["expiry"]:
            del TOKEN_MAP[token]  
            return False
        return True

    # --- Authentication ---
    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def api_login(self, **kwargs):
        try:
            db = kwargs.get('db', request.env.cr.dbname)
            login = kwargs.get('login')
            password = kwargs.get('password')
            
            uid = request.session.authenticate(db, login, password)
            if not uid:
                return {"status": "error", "message": "Invalid credentials"}

            token = secrets.token_urlsafe(64)
            expiry = datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)
            TOKEN_MAP[token] = {
                "uid": uid,
                "expiry": expiry
            }

            return {
                "status": "success",
                "token": token,
                "user_id": uid,
                "expires_at": expiry.isoformat()
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

            
    @http.route('/api/auth/logout', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def api_logout(self, **kwargs):
        """Invalidate the user's token."""
        token = request.httprequest.headers.get("Authorization")
        if token and token in TOKEN_MAP:
            del TOKEN_MAP[token]  
        return {
            "status": "success",
            "message": "Logged out successfully"
        }

        
    # --- Task CRUD ---
    @http.route('/api/task/create', type='json', auth='none', methods=['POST'], csrf=False, cors='*')
    def create_task(self, **kwargs):
        try:
            token = request.httprequest.headers.get("Authorization")
            if not token:
                return {"jsonrpc": "2.0", "result": {"status": "error", "message": "Authorization token missing"}}

            if token not in TOKEN_MAP or datetime.now() > TOKEN_MAP[token]["expiry"]:
                return {"jsonrpc": "2.0", "result": {"status": "error", "message": "Invalid or expired token"}}

            params = kwargs
            if not params:
                return {"jsonrpc": "2.0", "result": {"status": "error", "message": "No parameters provided"}}


            required_fields = ['name', 'project_id', 'stage_id']
            for field in required_fields:
                if field not in params:
                    return {
                        "jsonrpc": "2.0",
                        "result": {
                            "status": "error",
                            "message": f"Missing required field: {field}"
                        }
                    }

            task = request.env['project.task'].sudo().create({
                'name': params['name'],
                'project_id': params['project_id'],
                'stage_id': params['stage_id'],
                'user_ids': [(6, 0, params.get('user_ids', []))],
                'description': params.get('description', ''),
                'date_deadline': params.get('date_deadline'),
                'company_id': params.get('company_id', 1)
            })

            return {
                "jsonrpc": "2.0",
                "result": {
                    "status": "success",
                    "task_id": task.id,
                    "message": "Task created successfully"
                }
            }

        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "result": {
                    "status": "error",
                    "message": f"Server error: {str(e)}"
                }
            }

    

    
    @http.route('/api/project/task/<int:task_id>', type='json', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_task(self, task_id):
        token = request.httprequest.headers.get("Authorization")
        if not self._validate_token(token):
            return {"status": "error", "message": "Unauthorized", "code": 401}, 401

        task = request.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return {"status": "error", "message": "Task not found", "code": 404}, 404

        return {
            "id": task.id,
            "name": task.name,
            "description": task.description,
            "project_id": task.project_id.id,
            "user_ids": task.user_ids.ids,
            "date_deadline": task.date_deadline
        }

    @http.route('/api/project/tasks', type='json', auth='none', methods=['GET'], csrf=False, cors='*')
    def get_all_tasks(self, **kwargs):
        
        token = request.httprequest.headers.get("Authorization")
        if not token or token not in TOKEN_MAP:
            return {
                "status": "error",
                "message": "Unauthorized",
                "code": 401
            }, 401
        
        try:
            tasks = request.env['project.task'].sudo().search_read(
                [],
                ['id', 'name', 'description', 'project_id', 'user_ids', 'date_deadline']
            )
            
           
            return {
                "status": "success",
                "count": len(tasks),
                "tasks": tasks
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "code": 500
            }, 500
    @http.route('/api/project/task/update/<int:task_id>', type='json', auth='none', methods=['PUT'], csrf=False, cors='*')
    def update_task(self, task_id, **kwargs):
        token = request.httprequest.headers.get("Authorization")
        if not self._validate_token(token):
            return {"status": "error", "message": "Unauthorized", "code": 401}, 401

        task = request.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return {"status": "error", "message": "Task not found", "code": 404}, 404

        try:
            task.write({
                'name': kwargs.get('name', task.name),
                'description': kwargs.get('description', task.description),
                'project_id': kwargs.get('project_id', task.project_id.id),
                'user_ids': [(6, 0, kwargs.get('user_ids', task.user_ids.ids))],
                'date_deadline': kwargs.get('date_deadline', task.date_deadline)
            })
            return {"status": "success"}

        except Exception as e:
            return {"status": "error", "message": str(e), "code": 400}, 400

    @http.route('/api/project/task/delete/<int:task_id>', type='json', auth='none', methods=['DELETE'], csrf=False, cors='*')
    def delete_task(self, task_id):
        token = request.httprequest.headers.get("Authorization")
        if not self._validate_token(token):
            return {"status": "error", "message": "Unauthorized", "code": 401}, 401

        task = request.env['project.task'].sudo().browse(task_id)
        if not task.exists():
            return {"status": "error", "message": "Task not found", "code": 404}, 404

        task.unlink()
        return {"status": "success"}