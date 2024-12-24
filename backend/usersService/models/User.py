import bcrypt
from .db_connection import get_db_connection


class User:
    def __init__(self, user_id=None, username=None, email=None, password=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password = password

    @staticmethod
    def get_all_users():
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email FROM `User`")
            users = cursor.fetchall()
            return users
        except Exception as e:
            raise Exception(f"Error fetching users: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_user_by_id(user_id):
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email FROM `User` WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            if not user:
                raise Exception("User not found")
            return User(user_id=user['id'], username=user['username'], email=user['email'])
        except Exception as e:
            raise Exception(f"Error fetching user: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def get_by_email(email):
        """Fetch a user by their email."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT id, username, email, password FROM `User` WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data:
                return User(
                    user_id=user_data['id'],
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password']
                )
            return None  # Return None if no user is found
        except Exception as e:
            raise Exception(f"Error fetching user by email: {e}")
        finally:
            if connection:
                connection.close()


    def save(self):
        """Save a new user to the database."""
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO `User` (username, email, password)
                VALUES (%s, %s, %s)
            """, (self.username, self.email, hashed_password))
            connection.commit()
            self.id = cursor.lastrowid
        except Exception as e:
            raise Exception(f"Error saving user: {e}")
        finally:
            if connection:
                connection.close()

    def update(self, username=None, email=None, password=None):
        """Update user details in the database."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            query = "UPDATE `User` SET "
            params = []

            if username:
                query += "`username` = %s, "
                params.append(username)
            if email:
                query += "`email` = %s, "
                params.append(email)
            if password:
                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                query += "`password` = %s, "
                params.append(hashed_password)

            query = query.rstrip(", ")  # Remove trailing comma
            query += " WHERE `id` = %s"
            params.append(self.id)

            cursor.execute(query, tuple(params))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error updating user: {e}")
        finally:
            if connection:
                connection.close()

    @staticmethod
    def authenticate(email, password):
        """Authenticate a user by email and password."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT id, username, email, password FROM `User` WHERE email = %s", (email,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
                return User(user_id=user[0], username=user[1], email=user[2])
            return None
        except Exception as e:
            raise Exception(f"Error authenticating user: {e}")
        finally:
            if connection:
                connection.close()
