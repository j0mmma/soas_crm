from flask import Flask, jsonify, request
import mysql.connector
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'rootroot',
    'database': 'service_registry'
}

def get_db_connection():
    """Establish a database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/services', methods=['GET'])
def get_services():
    """Endpoint to fetch and display all services."""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM service")
        services = cursor.fetchall()
        print("Fetched services:", services)
        return jsonify(services), 200
    except mysql.connector.Error as err:
        print(f"Error fetching services: {err}")
        return jsonify({'error': 'Failed to fetch services'}), 500
    finally:
        connection.close()

@app.route('/services/register', methods=['POST'])
def register_service():
    """Endpoint to register a new service."""
    data = request.get_json()
    name = data.get('name')
    version = data.get('version')
    url = data.get('url')

    if not name or not version or not url:
        return jsonify({'error': 'Missing required fields: name, version, url'}), 400

    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

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
        """, (name, version, url, current_time))
        connection.commit()
        return jsonify({'message': f"Service '{name}' registered successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error registering service: {err}")
        return jsonify({'error': 'Failed to register service'}), 500
    finally:
        connection.close()

@app.route('/services/deregister/<string:name>', methods=['POST'])
def deregister_service(name):
    """Endpoint to deregister a service."""
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            UPDATE service
            SET last_closed = %s, running = FALSE
            WHERE name = %s
        """, (current_time, name))
        connection.commit()
        if cursor.rowcount == 0:
            return jsonify({'message': f"Service '{name}' not found"}), 404
        return jsonify({'message': f"Service '{name}' deregistered successfully"}), 200
    except mysql.connector.Error as err:
        print(f"Error deregistering service: {err}")
        return jsonify({'error': 'Failed to deregister service'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(port=5002)
