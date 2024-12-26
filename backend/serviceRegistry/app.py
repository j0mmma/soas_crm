from flask import Flask, jsonify
import mysql.connector

# Flask app
app = Flask(__name__)

# Database configuration
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
        print("Fetched services:", services)  # Log to console
        return jsonify(services), 200
    except mysql.connector.Error as err:
        print(f"Error fetching services: {err}")
        return jsonify({'error': 'Failed to fetch services'}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(port=5002)
