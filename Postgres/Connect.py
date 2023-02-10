import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

def connect(unitTest = False):
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = {
            'host': os.getenv('DB_HOST'),
            'database': os.getenv('DB_NAME'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'port': os.getenv('DB_PORT')
        }
        conn = psycopg2.connect(**params)
        if unitTest:
            print('Database connection successful.')
            cursor = conn.cursor();
            print("PostgreSQL server version:", cursor.fetchone())
            cursor.close()
            return conn
        # create a cursor
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error);