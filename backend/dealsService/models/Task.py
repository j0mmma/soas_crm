from .db_connection import get_db_connection

class Task:
    @staticmethod
    def create_task(title, description, done, deal_id, assignee_id, due):
        """Create a new task associated with a deal."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Task (title, description, done, deal_id, assignee_id, due)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (title, description, done, deal_id, assignee_id, due))
            connection.commit()
            return cursor.lastrowid
        except Exception as e:
            raise Exception(f"Error creating task: {e}")
        finally:
            connection.close()

    @staticmethod
    def get_tasks_by_deal(deal_id):
        """Fetch all tasks for a specific deal."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT * FROM Task WHERE deal_id = %s
            """, (deal_id,))
            return cursor.fetchall()
        except Exception as e:
            raise Exception(f"Error fetching tasks: {e}")
        finally:
            connection.close()

    @staticmethod
    def delete_task(task_id):
        """Delete a task by its ID."""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("DELETE FROM Task WHERE id = %s", (task_id,))
            connection.commit()
        except Exception as e:
            raise Exception(f"Error deleting task: {e}")
        finally:
            connection.close()

    @staticmethod
    def update_task_done(task_id, done):
        """Update the 'done' status of a task by its ID"""
        connection = get_db_connection()
        try:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Task
                SET done = %s
                WHERE id = %s
            """, (done, task_id))
            connection.commit()

            if cursor.rowcount == 0:
                return False  
            return True
        except Exception as e:
            raise Exception(f"Error updating task status: {e}")
        finally:
            connection.close()
