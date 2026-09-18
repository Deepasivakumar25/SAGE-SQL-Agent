import psycopg2


def get_connection():
    connection = psycopg2.connect(
        host="localhost",
        database="company_db",
        user="postgres",
        password="Deepa@19950125"
    )

    return connection