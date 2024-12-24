from .db_connection import get_db_connection

class Team:
    def __init__(self, team_id=None, name=None, owner_id=None, owner_name=None, members=None):
        self.team_id = team_id
        self.name = name
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.members = members or []

    @staticmethod
    def get_team_info_by_user_id(user_id):
        """Fetch team-related info for a specific user."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT t.id AS team_id, t.name, t.owner_id, u.username AS owner_name
                FROM `Team_User` tu
                JOIN `Team` t ON tu.team_id = t.id
                LEFT JOIN `User` u ON t.owner_id = u.id
                WHERE tu.user_id = %s
            """, (user_id,))
            team_info = cursor.fetchone()
            if team_info:
                return Team(
                    team_id=team_info['team_id'],
                    name=team_info['name'],
                    owner_id=team_info['owner_id'],
                    owner_name=team_info['owner_name']
                )
            return None
        except Exception as e:
            raise Exception(f"Error fetching team info: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def create_team(name, owner_id):
        """Create a new team and add the owner to the team_user table."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            # Insert the new team
            cursor.execute("""
                INSERT INTO `Team` (name, owner_id)
                VALUES (%s, %s)
            """, (name, owner_id))
            connection.commit()
            team_id = cursor.lastrowid

            # Add the owner to the team_user table
            cursor.execute("""
                INSERT INTO `Team_User` (team_id, user_id, role_id, status_id)
                VALUES (%s, %s, 2, 1)  -- Role 2 = Admin, Status 1 = Active
            """, (team_id, owner_id))
            connection.commit()

            return team_id
        except Exception as e:
            raise Exception(f"Error creating team: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def add_user_to_team(team_id, user_id):
        """Add a user to a team."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO `Team_User` (team_id, user_id, role_id, status_id)
                VALUES (%s, %s, 1, 1)  -- Role 1 = Member, Status 1 = Active
            """, (team_id, user_id))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error adding user to team: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def remove_user_from_team(team_id, user_id):
        """Remove a user from a team."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM `Team_User` WHERE team_id = %s AND user_id = %s", (team_id, user_id))
            connection.commit()
            if cursor.rowcount == 0:
                raise Exception("User not found in the team.")
        except Exception as e:
            raise Exception(f"Error removing user from team: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_team_members(team_id):
        """Fetch all members of a team, including their roles and statuses."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    u.id AS user_id, 
                    u.username, 
                    u.email, 
                    tu.role_id, 
                    ur.name AS role_name,
                    tu.status_id,
                    us.name AS status_name
                FROM `Team_User` tu
                JOIN `User` u ON tu.user_id = u.id
                LEFT JOIN `UserRole` ur ON tu.role_id = ur.id
                LEFT JOIN `UserStatus` us ON tu.status_id = us.id
                WHERE tu.team_id = %s
            """, (team_id,))
            members = cursor.fetchall()
            return members
        except Exception as e:
            raise Exception(f"Error fetching team members: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def delete_team(team_id):
        """Delete a team and all associated entries in Team_User."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            # Delete from Team_User first
            cursor.execute("DELETE FROM `Team_User` WHERE team_id = %s", (team_id,))
            # Delete the team
            cursor.execute("DELETE FROM `Team` WHERE id = %s", (team_id,))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error deleting team: {e}")
        finally:
            if connection:
                connection.close()
