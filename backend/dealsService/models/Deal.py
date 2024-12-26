from .db_connection import get_db_connection

class Deal:
    def __init__(self, id=None, title=None, stage_id=None, owner_id=None, team_id=None, date_created=None):
        self.id = id
        self.title = title
        self.stage_id = stage_id
        self.owner_id = owner_id
        self.team_id = team_id
        self.date_created = date_created

    @staticmethod
    def get_deal_by_id(deal_id):
        """Fetch a deal by its ID, including its stage and associated contacts."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT d.id, d.title, d.owner_id, d.team_id, d.date_created, s.name AS stage_name
                FROM Deal d
                JOIN Stage s ON d.stage_id = s.id
                WHERE d.id = %s
            """, (deal_id,))
            deal = cursor.fetchone()
            if not deal:
                return None

            cursor.execute("""
                SELECT c.id AS contact_id, c.firstName, c.lastName, c.email, c.phone
                FROM Deal_Contact dc
                JOIN Contact c ON dc.contact_id = c.id
                WHERE dc.deal_id = %s
            """, (deal_id,))
            contacts = cursor.fetchall()

            deal['contacts'] = contacts
            return deal
        except Exception as e:
            raise Exception(f"Error fetching deal by ID: {e}")
        finally:
            if connection:
                connection.close()


    @staticmethod
    def get_all_deals_by_team(team_id):
        """Fetch all deals for a specific team."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, title, stage_id, owner_id, team_id, date_created
                FROM Deal
                WHERE team_id = %s
            """, (team_id,))
            deals = cursor.fetchall()
            return [Deal(**deal) for deal in deals]
        except Exception as e:
            raise Exception(f"Error fetching deals: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def create_new_deal(title, stage_id, owner_id, team_id):
        """Create a new deal."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Deal (title, stage_id, owner_id, team_id)
                VALUES (%s, %s, %s, %s)
            """, (title, stage_id, owner_id, team_id))
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            raise Exception(f"Error creating deal: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_all_stages():
        """Fetch all stages from the database."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, name FROM Stage")
            stages = cursor.fetchall()
            return stages
        except Exception as e:
            raise Exception(f"Error fetching stages: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def delete_deal(deal_id):
        """Delete a deal along with its associated contacts and tasks."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Task WHERE deal_id = %s", (deal_id,))
            cursor.execute("DELETE FROM Deal_Contact WHERE deal_id = %s", (deal_id,))
            cursor.execute("DELETE FROM Deal WHERE id = %s", (deal_id,))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error deleting deal: {e}")
        finally:
            if connection:
                connection.close()
