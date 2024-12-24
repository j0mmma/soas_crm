from flask import Blueprint, jsonify, request
from models.Contact import Contact
from .utils import token_required


class ContactController:
    def __init__(self):
        self.blueprint = Blueprint('contacts', __name__)
        self.register_routes()

    def register_routes(self):
        self.blueprint.add_url_rule('/<int:deal_id>', 'get_contacts', self.get_contacts, methods=['GET'])
        self.blueprint.add_url_rule('/create', 'create_contact', self.create_contact, methods=['POST'])





    @token_required
    def get_contacts(self, deal_id):
        """Get all contacts for a specific deal."""
        try:
            contacts = Contact.get_contacts_by_deal(deal_id)
            return jsonify([contact.__dict__ for contact in contacts]), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @token_required
    def create_contact(self):
        """Create a new contact and associate it with a deal."""
        try:
            data = request.get_json()
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            email = data.get('email')
            phone = data.get('phone')
            team_id = request.user.get('team_id')  # Extract team ID from token
            deal_id = data.get('deal_id')

            if not email or not team_id or not deal_id:
                return jsonify({'message': 'Email, team_id, and deal_id are required'}), 400

            contact_id = Contact.create_contact(first_name, last_name, email, phone, team_id, deal_id)
            return jsonify({'message': 'Contact created successfully!', 'contact_id': contact_id}), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500
