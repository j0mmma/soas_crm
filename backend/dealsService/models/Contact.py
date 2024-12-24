from .db_connection import get_db_connection


class Contact:
    def __init__(self, contact_id=None, first_name=None, last_name=None, email=None, phone=None, team_id=None):
        self.contact_id = contact_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.team_id = team_id

    @staticmethod
    def get_contacts_by_deal(deal_id):
        """Fetch all contacts associated with a specific deal."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    c.id AS contact_id, 
                    c.firstName AS first_name, 
                    c.lastName AS last_name, 
                    c.email, 
                    c.phone
                FROM Deal_Contact dc
                JOIN Contact c ON dc.contact_id = c.id
                WHERE dc.deal_id = %s
            """, (deal_id,))
            contacts = cursor.fetchall()
            return [Contact(**contact) for contact in contacts]
        except Exception as e:
            raise Exception(f"Error fetching contacts: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def create_contact(first_name, last_name, email, phone, team_id, deal_id):
        """Create a new contact and associate it with a deal."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            # Insert new contact
            cursor.execute("""
                INSERT INTO Contact (firstName, lastName, email, phone, team_id)
                VALUES (%s, %s, %s, %s, %s)
            """, (first_name, last_name, email, phone, team_id))
            connection.commit()
            contact_id = cursor.lastrowid

            # Associate contact with deal
            cursor.execute("""
                INSERT INTO Deal_Contact (deal_id, contact_id)
                VALUES (%s, %s)
            """, (deal_id, contact_id))
            connection.commit()

            return contact_id
        except Exception as e:
            raise Exception(f"Error creating contact: {e}")
        finally:
            if connection:
                connection.close()
