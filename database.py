import psycopg2
from psycopg2 import sql

import os

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
def insert(connection, table_name, columns, data_iterator):
    # Exclude the 'id' column since it's auto-incremented
    columns = [col for col in columns if col != 'id']
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

# Sample usage
def main():
    # Define your PostgreSQL connection parameters
    conn_params = {
        "dbname": os.getenv("POSTGRES_DATABASE").strip("\""),
        "user": os.getenv("POSTGRES_USER").strip("\""),
        "password": os.getenv("POSTGRES_PASSWORD").strip("\""),
        "host": os.getenv("POSTGRES_HOST").strip("\""),
        "port": "5432"
    }

    print("Connecting to the PostgreSQL database...")

    # Connect to the PostgreSQL database
    connection = psycopg2.connect(**conn_params)

    # Define table name and columns
    table_name = 'test_table'
    columns = {
        'id': 'SERIAL PRIMARY KEY',
        'name': 'VARCHAR(100)',
        'age': 'INT',
        'email': 'VARCHAR(100)'
    }

    # Sample data iterator (e.g., can be a generator or list of tuples)
    data_iterator = [
        ('Alice', 30, 'alice@example.com'),
        ('Bob', 25, 'bob@example.com'),
        ('Charlie', 35, 'charlie@example.com')
    ]

    try:
        # Create table if it doesn't exist
        create_table_if_not_exists(connection, table_name, columns)

        # Insert data from iterator
        insert(connection, table_name, columns.keys(), data_iterator)
        print("Data inserted successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        connection.close()

if __name__ == "__main__":
    main()
