import mysql.connector
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rootroot',
    'database': 'service_registry'
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

class ServiceRegistry:
    def __init__(self, name, version, url):
        self.name = name
        self.version = version
        self.url = url

    def register_service(self):
        """Register or update the service in the registry and set it as running."""
        connection = get_db_connection()
        if not connection:
            print("Database connection failed")
            return False

        try:
            cursor = connection.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO service (name, version, url, last_registered, running)
                VALUES (%s, %s, %s, %s, TRUE)
                ON DUPLICATE KEY UPDATE
                version = VALUES(version),
                url = VALUES(url),
                last_registered = VALUES(last_registered),
                running = TRUE
            """, (self.name, self.version, self.url, current_time))
            connection.commit()
            print(f"Service '{self.name}' registered successfully and set to running.")
            return True
        except mysql.connector.Error as err:
            print(f"Error registering service: {err}")
            return False
        finally:
            connection.close()

    def deregister_service(self):
        """Deregister the service from the registry and set it as not running."""
        connection = get_db_connection()
        if not connection:
            print("Database connection failed")
            return False

        try:
            cursor = connection.cursor()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                UPDATE service
                SET last_closed = %s, running = FALSE
                WHERE name = %s
            """, (current_time, self.name))
            connection.commit()
            print(f"Service '{self.name}' deregistered successfully and set to not running.")
            return True
        except mysql.connector.Error as err:
            print(f"Error deregistering service: {err}")
            return False
        finally:
            connection.close()
