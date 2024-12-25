from flask import Blueprint, request, jsonify
from models.Task import Task
from .utils import token_required

class TaskController:
    def __init__(self):
        self.blueprint = Blueprint('tasks', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule('/<int:deal_id>', 'get_tasks', self.get_tasks_by_deal, methods=['GET'])
        self.blueprint.add_url_rule('/create', 'create_task', self.create_task, methods=['POST'])
        self.blueprint.add_url_rule('/delete/<int:task_id>', 'delete_task', self.delete_task, methods=['DELETE'])
        self.blueprint.add_url_rule('/update-status/<int:task_id>', 'update_task_status', self.update_task_status, methods=['PATCH'])

    @token_required
    def get_tasks_by_deal(self, deal_id):
        """Get all tasks for a specific deal."""
        try:
            tasks = Task.get_tasks_by_deal(deal_id)
            return jsonify(tasks), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def create_task(self):
        """Create a new task for a deal."""
        try:
            data = request.get_json()
            title = data.get('title')
            description = data.get('description', '')
            done = data.get('done', False)
            deal_id = data.get('deal_id')
            assignee_id = data.get('assignee_id')
            due = data.get('due')

            if not title or not deal_id or not assignee_id:
                return jsonify({'message': 'Title, deal_id, and assignee_id are required'}), 400

            task_id = Task.create_task(title, description, done, deal_id, assignee_id, due)
            return jsonify({'message': 'Task created successfully', 'task_id': task_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def delete_task(self, task_id):
        """Delete a task by ID."""
        try:
            Task.delete_task(task_id)
            return jsonify({'message': 'Task deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def update_task_status(self, task_id):
        """Update the 'done' status of a task."""
        try:
            data = request.get_json()
            done = data.get('done')

            if done is None:
                return jsonify({'message': "'done' field is required"}), 400

            updated = Task.update_task_done(task_id, done)

            if not updated:
                return jsonify({'message': 'Task not found'}), 404

            return jsonify({'message': 'Task status updated successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500