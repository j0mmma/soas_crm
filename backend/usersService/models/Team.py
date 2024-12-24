from .db_connection import get_db_connection


class Team:
    def __init__(self, team_id=None, owner_id=None, role_id=None):
        self.team_id = team_id
        self.owner_id = owner_id
        self.role_id = role_id

    @staticmethod
    def get_team_info_by_user_id(user_id):
        """Fetch team-related info for a specific user."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT tu.team_id, tu.role_id, t.owner_id 
                FROM `Team_User` tu 
                LEFT JOIN `Team` t ON tu.team_id = t.id
                WHERE tu.user_id = %s
            """, (user_id,))
            team_info = cursor.fetchone()
            if team_info:
                return Team(
                    team_id=team_info['team_id'],
                    owner_id=team_info['owner_id'],
                    role_id=team_info['role_id']
                )
            return None
        except Exception as e:
            raise Exception(f"Error fetching team info: {e}")
        finally:
            if connection:
                connection.close()
