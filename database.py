import psycopg2
from psycopg2 import sql

import os

def get_connection():
    # Define your PostgreSQL connection parameters
    conn_params = {
        "dbname": os.getenv("POSTGRES_DATABASE").strip("\""),
        "user": os.getenv("POSTGRES_USER").strip("\""),
        "password": os.getenv("POSTGRES_PASSWORD").strip("\""),
        "host": os.getenv("POSTGRES_HOST").strip("\""),
        "port": "5432"
    }

    # Connect to the PostgreSQL database
    connection = psycopg2.connect(**conn_params)
    return connection

# Function to create a table if it does not exist
def create_table_if_not_exists(connection, table_name, columns):
    with connection.cursor() as cursor:
        # Dynamically generate the CREATE TABLE query
        create_table_query = sql.SQL(
            """
            CREATE TABLE IF NOT EXISTS {table} (
                {columns}
            );
            """
        ).format(
            table=sql.Identifier(table_name),
            columns=sql.SQL(", ").join([
                sql.SQL("{} {}").format(sql.Identifier(col_name), sql.SQL(col_type))
                for col_name, col_type in columns.items()
            ])
        )
        cursor.execute(create_table_query)
        connection.commit()

# Function to insert data into the table
def insert(table_name, entity, data_iterator, auto_increment=True):
    connection = get_connection()
    skip_id= 1 if auto_increment else 0
    columns = entity.__init__.__code__.co_varnames[1 + skip_id:]
    with connection.cursor() as cursor:
        # Prepare the INSERT query dynamically
        insert_query = sql.SQL(
            """
            INSERT INTO {table} ({fields})
            VALUES ({placeholders})
            """
        ).format(
            table=sql.Identifier(table_name),
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            placeholders=sql.SQL(', ').join(sql.Placeholder() * len(columns))
        )

        for row in data_iterator:
            cursor.execute(insert_query, row)
        connection.commit()
    connection.close()

def select(table_name, entity):   
    items = []
    connection = get_connection()
    columns = entity.__init__.__code__.co_varnames[1:]
    with connection.cursor() as cursor:
        # Prepare the SELECT query dynamically
        select_query = sql.SQL(
            """
            SELECT {fields}
            FROM {table}
            """
        ).format(
            fields=sql.SQL(', ').join(map(sql.Identifier, columns)),
            table=sql.Identifier(table_name)
        )
        cursor.execute(select_query)
        rows = cursor.fetchall()
        items = [dict(zip(columns, values)) for values in rows]        
    connection.close()
    return items
    

