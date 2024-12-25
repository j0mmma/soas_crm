from flask import Blueprint, request, jsonify
from models.Deal import Deal
from .utils import token_required

class DealController:
    def __init__(self):
        self.blueprint = Blueprint('deals', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule('/all', 'get_deals_by_team', self.get_deals, methods=['GET'])
        self.blueprint.add_url_rule('/create', 'create_deal', self.create_deal, methods=['POST'])
        self.blueprint.add_url_rule('/<int:deal_id>', 'get_deal_by_id', self.get_deal_by_id, methods=['GET'])
        self.blueprint.add_url_rule('/stages', 'get_all_stages', self.get_all_stages, methods=['GET'])
        self.blueprint.add_url_rule('/delete/<int:deal_id>', 'delete_deal', self.delete_deal, methods=['DELETE'])



    @token_required
    def get_deal_by_id(self, deal_id):
        """Fetch a specific deal by ID, including its stage and associated contacts."""
        try:
            # Fetch deal details
            deal = Deal.get_deal_by_id(deal_id)
            if not deal:
                return jsonify({'error': 'Deal not found'}), 404

            return jsonify(deal), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @token_required
    def get_deals(self):
        """Get all deals for the current user's team."""
        try:
            # Extract the team_id from the token
            team_id = request.user.get('team_id')

            if not team_id:
                return jsonify({'error': 'User is not associated with any team'}), 403

            deals = Deal.get_all_deals_by_team(team_id)
            return jsonify([deal.__dict__ for deal in deals]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def create_deal(self):
        """Create a new deal."""
        try:
            data = request.get_json()
            title = data.get('title')
            stage_id = data.get('stage_id')
            owner_id = request.user['user_id']  # Extracted from token
            team_id = request.user['team_id']  # Extracted from token

            if not title or not stage_id:
                return jsonify({'message': 'Title and stage_id are required'}), 400

            deal_id = Deal.create_new_deal(title, stage_id, owner_id, team_id)
            return jsonify({'message': 'Deal created successfully', 'deal_id': deal_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def get_all_stages(self):
        """Fetch all stages."""
        try:
            stages = Deal.get_all_stages()
            return jsonify(stages), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def delete_deal(self, deal_id):
        """Delete a deal if the current user is the owner."""
        try:
            user_id = request.user['user_id']  # Extract user ID from token

            # Fetch the deal details
            deal = Deal.get_deal_by_id(deal_id)
            if not deal:
                return jsonify({'message': 'Deal not found'}), 404

            # Check if the current user is the owner
            if deal['owner_id'] != user_id:
                return jsonify({'message': 'You do not have permission to delete this deal'}), 403

            # Delete the deal
            Deal.delete_deal(deal_id)
            return jsonify({'message': 'Deal deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
