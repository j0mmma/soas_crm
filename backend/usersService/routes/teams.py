from flask import Blueprint, request, jsonify, abort
from flask_login import login_required, current_user
from db_connection import get_db_connection

team_routes = Blueprint('teams', __name__)

# Helper function to check if user is owner
def is_team_owner(team_id, user_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT `owner_id` FROM `Team` WHERE `id` = %s", (team_id,))
        result = cursor.fetchone()
        return result and result[0] == user_id
    finally:
        if connection:
            connection.close()

# Helper function to check if user is admin
def is_team_admin(team_id, user_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT `role_id` FROM `Team_User` 
            WHERE `team_id` = %s AND `user_id` = %s
        """, (team_id, user_id))
        result = cursor.fetchone()
        return result and result[0] == 2  # Assuming '2' is the role_id for admin
    finally:
        if connection:
            connection.close()

# Get all teams
@team_routes.route('/', methods=['GET'])
def get_all_teams():
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT t.id, t.name, u.id AS owner_id, u.username AS owner_name
            FROM `Team` t
            LEFT JOIN `User` u ON t.owner_id = u.id
        """
        cursor.execute(query)
        teams = cursor.fetchall()
        return jsonify(teams), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# Get team by ID
@team_routes.route('/<int:team_id>', methods=['GET'])
def get_team_by_id(team_id):
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT t.id, t.name, u.id AS owner_id, u.username AS owner_name
            FROM `Team` t
            LEFT JOIN `User` u ON t.owner_id = u.id
            WHERE t.id = %s
        """
        cursor.execute(query, (team_id,))
        team = cursor.fetchone()
        if team:
            return jsonify(team), 200
        return jsonify({'message': 'Team not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# TODO: this needs to add respective entry to Team_user
@team_routes.route('/', methods=['POST'])
@login_required
def create_team():
    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    name = data.get('name')

    if not name:
        return jsonify({'message': 'Missing required field: name'}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()

        # Insert the new team into the Team table
        cursor.execute("INSERT INTO `Team` (`name`, `owner_id`) VALUES (%s, %s)", (name, current_user.id))
        connection.commit()

        # Get the ID of the newly created team
        team_id = cursor.lastrowid

        # Add the creator to the Team_User table as admin with active status
        ADMIN_ROLE_ID = 2  # Assuming '2' is the role_id for admin
        ACTIVE_STATUS_ID = 1  # Assuming '1' is the status_id for active
        cursor.execute("""
            INSERT INTO `Team_User` (`team_id`, `user_id`, `role_id`, `status_id`) 
            VALUES (%s, %s, %s, %s)
        """, (team_id, current_user.id, ADMIN_ROLE_ID, ACTIVE_STATUS_ID))
        connection.commit()

        return jsonify({'message': 'Team created successfully!', 'team_id': team_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()




# Delete a team
@team_routes.route('/<int:team_id>', methods=['DELETE'])
@login_required
def delete_team(team_id):
    if not is_team_owner(team_id, current_user.id):
        return jsonify({'message': 'Only the team owner can delete the team'}), 403

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM `Team` WHERE `id` = %s", (team_id,))
        connection.commit()
        return jsonify({'message': 'Team deleted successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# TODO: fix
# Update a team
@team_routes.route('/<int:team_id>', methods=['PUT'])
@login_required
def update_team(team_id):
    if not is_team_admin(team_id, current_user.id):
        return jsonify({'message': 'Only admins can update the team'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    name = data.get('name')
    if not name:
        return jsonify({'message': 'No fields to update'}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("UPDATE `Team` SET `name` = %s WHERE `id` = %s", (name, team_id))
        connection.commit()
        return jsonify({'message': 'Team updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# Add user to team
@team_routes.route('/<int:team_id>/add_user', methods=['POST'])
@login_required
def add_user_to_team(team_id):
    if not is_team_admin(team_id, current_user.id):
        return jsonify({'message': 'Only admins can add users to the team'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    user_id = data.get('user_id')
    role_id = data.get('role_id')
    status_id = data.get('status_id')

    if not user_id or not role_id or not status_id:
        return jsonify({'message': 'Missing required fields'}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO `Team_User` (`team_id`, `user_id`, `role_id`, `status_id`)
            VALUES (%s, %s, %s, %s)
        """, (team_id, user_id, role_id, status_id))
        connection.commit()
        return jsonify({'message': 'User added to team successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()

# Remove user from team
@team_routes.route('/<int:team_id>/remove_user/<int:user_id>', methods=['DELETE'])
@login_required
def remove_user_from_team(team_id, user_id):
    if not is_team_admin(team_id, current_user.id):
        return jsonify({'message': 'Only admins can remove users from the team'}), 403

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM `Team_User` WHERE `team_id` = %s AND `user_id` = %s", (team_id, user_id))
        connection.commit()
        return jsonify({'message': 'User removed from team successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()


# TODO: fix
@team_routes.route('/<int:team_id>/members', methods=['GET'])
@login_required
def list_team_members(team_id):
    print(f"Current user: {current_user}")  # Debugging line
    connection = get_db_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT u.id, u.username, u.email, tu.role_id 
            FROM `User` u 
            JOIN `Team_User` tu ON u.id = tu.user_id 
            WHERE tu.team_id = %s
        """
        cursor.execute(query, (team_id,))
        members = cursor.fetchall()
        if not members:
            return jsonify({'message': f'No members found for team {team_id}'}), 404
        return jsonify(members), 200
    except Exception as e:
        print(f"Error fetching team members: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()



# Change user role in a team
@team_routes.route('/<int:team_id>/change_role/<int:user_id>', methods=['PUT'])
@login_required
def change_user_role(team_id, user_id):
    if not is_team_admin(team_id, current_user.id):
        return jsonify({'message': 'Only admins can change user roles'}), 403

    data = request.get_json()
    if not data:
        return jsonify({'message': 'Invalid JSON payload'}), 400

    new_role_id = data.get('role_id')
    if not new_role_id:
        return jsonify({'message': 'Missing required field: role_id'}), 400

    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE `Team_User` SET `role_id` = %s 
            WHERE `team_id` = %s AND `user_id` = %s
        """, (new_role_id, team_id, user_id))
        connection.commit()
        return jsonify({'message': 'User role updated successfully!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if connection:
            connection.close()