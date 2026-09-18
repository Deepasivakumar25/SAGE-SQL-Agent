from database import get_connection


def execute_sql(query: str):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        return f"SQL Error: {e}"

    finally:
        cursor.close()
        connection.close()
