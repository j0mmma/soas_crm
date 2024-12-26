from flask import Blueprint, jsonify, request
from models.Team import Team
from models.User import User
from .utils import token_required


class TeamController:
    def __init__(self):
        self.blueprint = Blueprint('teams', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule(
            '/my-team', 'get_my_team', self.get_my_team, methods=['GET'])
        self.blueprint.add_url_rule(
            '/add-user', 'add_user_to_team', self.add_user_to_team, methods=['POST'])
        self.blueprint.add_url_rule(
            '/remove-user', 'remove_user', self.remove_user, methods=['POST'])
        self.blueprint.add_url_rule('/delete', 'delete_team', self.delete_team, methods=['DELETE'])
        self.blueprint.add_url_rule('/new', 'create_team', self.create_team, methods=['POST']
)


    @token_required
    def get_my_team(self):
        """Get the current user's team info including name, owner, and members."""
        try:
            user_id = request.user['user_id'] 
            team = Team.get_team_info_by_user_id(user_id)

            if not team:
                return jsonify({'message': 'User is not part of any team'}), 404

            team.members = Team.get_team_members(team.team_id)

            return jsonify({
                'team_id': team.team_id,
                'team_name': team.name,
                'owner_id': team.owner_id,
                'owner_name': team.owner_name,
                'members': team.members
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def add_user_to_team(self):
        """Add a user to the current user's team."""
        try:
            user_id = request.user['user_id']  
            data = request.get_json()
            email = data.get('email')

            if not email:
                return jsonify({'message': 'Email is required'}), 400

            team_info = Team.get_team_info_by_user_id(user_id)
            if not team_info:
                return jsonify({'message': 'You are not part of any team'}), 403

            current_user_role = next(
                (member for member in Team.get_team_members(team_info.team_id) if member['user_id'] == user_id), None
            )
            if not current_user_role or current_user_role['role_name'] != 'Admin':
                return jsonify({'message': 'Only admins can add users to the team'}), 403

            new_user = User.get_by_email(email)
            if not new_user:
                return jsonify({'message': "User with this email doesn't exist"}), 404

            user_team = Team.get_team_info_by_user_id(new_user.id)
            if user_team:
                return jsonify({'message': 'This user is already part of another team'}), 403

            Team.add_user_to_team(team_info.team_id, new_user.id)
            return jsonify({'message': 'User added to the team successfully!'}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def remove_user(self):
        """Remove a user from the team."""
        try:
            current_user_id = request.user['user_id']
            data = request.get_json()

            team_id = data.get('team_id')
            user_id_to_remove = data.get('user_id')

            if not team_id or not user_id_to_remove:
                return jsonify({'message': 'Team ID and User ID are required.'}), 400

            team_info = Team.get_team_info_by_user_id(current_user_id)

            if not team_info:
                return jsonify({'message': 'You are not part of any team.'}), 403

            is_admin = any(
                member['user_id'] == current_user_id and member['role_name'] == 'Admin'
                for member in Team.get_team_members(team_id)
            )

            if not is_admin:
                return jsonify({'message': 'You do not have the rights to remove users from this team.'}), 403

            if user_id_to_remove == team_info.owner_id:
                return jsonify({'message': 'You cannot remove the owner of the team.'}), 403

            Team.remove_user_from_team(team_id, user_id_to_remove)
            return jsonify({'message': 'User removed from the team successfully.'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # TODO: FIX
    @token_required
    def delete_team(self):
        """Delete a team if the user is the owner."""
        try:
            user_id = request.user['user_id']
            team_id = request.user.get('team_id')
            is_owner = request.user.get('is_owner')

            if not team_id:
                return jsonify({'message': 'You are not associated with any team'}), 403

            if not is_owner:
                return jsonify({'message': 'You do not have permission to delete this team'}), 403

            # Delete the team
            Team.delete_team(team_id)
            return jsonify({'message': 'Team deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @token_required
    def create_team(self):
        """Create a new team and add the owner to the team_user table."""
        try:
            user_id = request.user['user_id'] 
            team_id = request.user.get('team_id') 

            if team_id:
                return jsonify({'message': 'You are already part of a team and cannot create a new one.'}), 403

            data = request.get_json()
            team_name = data.get('team_name')
            if not team_name:
                return jsonify({'message': 'Team name is required'}), 400

            try:
                team_id = Team.create_team(name=team_name, owner_id=user_id)
                return jsonify({'message': 'Team created successfully!', 'team_id': team_id}), 201
            except Exception as e:
                return jsonify({'message': str(e)}), 500

        except Exception as e:
            return jsonify({'error': str(e)}), 500

