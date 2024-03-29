import psycopg2
from dotenv import load_dotenv
import os


login_temp_query = """update user_creds 
set first_login = case 
	when first_login IS NULL then '{first_login}'
	else first_login  
end,
	last_login = '{last_login}'
where 
	email ='{email}' and
	password ='{password}';
"""


load_dotenv()

# Connection parameters
hostname = os.environ.get("DB_HOSTNAME")
username = os.environ.get("DB_USERNAME")
password = os.environ.get("DB_PASSWORD")
database_name = os.environ.get("DB_NAME")


def connect_db():
    """
    Establishes a connection to the PostgreSQL database.

    Returns:
        psycopg2.extensions.connection: Connection object to the database.
    """
    connection = psycopg2.connect(
        host=hostname,
        user=username,
        password=password,
        dbname=database_name
    )
    return connection