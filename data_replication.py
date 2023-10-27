import oracledb
import psycopg2
import os
from psycopg2.extras import execute_batch
import time
import json

oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_12")

# Read table information, source schema, and target schema from JSON file
json_file = os.environ['extract.json']
config_data = json.loads(json_file)
print(config_data)

## To-do: Pull the source and target metadata based on source-name from ODS (RRS, FTA) - follow IRS naming conventions
### source_database_name = os.environ['SOURCE']

# Extract configuration data
source_schema = config_data['init']['source_schema']
target_schema = config_data['init']['target_schema']
tables_to_extract = config_data['sor_object']

# record start time
start = time.time() 

# Retrieve Oracle database configuration
oracle_username = os.environ['DB_USERNAME']
oracle_password = os.environ['DB_PASSWORD']
oracle_host = os.environ['DB_HOST']
oracle_port = os.environ['DB_PORT']
oracle_database = os.environ['DATABASE']

# Retrieve Postgres database configuration
postgres_username = os.environ['ODS_USERNAME']
postgres_password = os.environ['ODS_PASSWORD']
postgres_host = os.environ['ODS_HOST']
postgres_port = os.environ['ODS_PORT']
postgres_database = os.environ['ODS_DATABASE']

# Set up Oracle database connection
dsn = oracledb.makedsn(host=oracle_host, port=oracle_port, service_name=oracle_database)
oracle_connection = oracledb.connect(user=oracle_username, password=oracle_password, dsn=dsn)
print("Is the connection thin:", oracle_connection.thin)
print('Oracle Connection Successful')

# Set up Postgres database connection
postgres_connection = psycopg2.connect(user=postgres_username, password=postgres_password,
                                      host=postgres_host, port=postgres_port, database=postgres_database)

print('Postgres Connection Successful')

# Create a cursor object to execute SQL queries for Oracle and Postgres
oracle_cursor = oracle_connection.cursor()
postgres_cursor = postgres_connection.cursor()

# Function to extract data from Oracle
def extract_from_oracle(table_name):
    try:
        # Use placeholders in the query and bind the table name as a parameter
        sql_query = f'SELECT * FROM {source_schema}.{table_name}'
        print(sql_query)
        oracle_cursor.execute(sql_query)
        rows = oracle_cursor.fetchall()
        return rows
    except Exception as e:
        print(f"Error extracting data from Oracle: {str(e)}")
        return []

# Function to load data into PostgreSQL using execute_batch
def load_into_postgres(table_name, data):
    try:
        # Delete existing data in the target table
        delete_query = f'TRUNCATE TABLE {target_schema}.{table_name}'
        postgres_cursor.execute(delete_query)

        # Build the INSERT query with placeholders
        insert_query = f'INSERT INTO {target_schema}.{table_name} VALUES ({", ".join(["%s"] * len(data[0]))})'
        #insert_query = f'INSERT INTO {target_schema}.{table_name} VALUES %s'

        # Use execute_batch for efficient batch insert
        with postgres_connection.cursor() as cursor:
            # Prepare the data as a list of tuples
            data_to_insert = [(tuple(row)) for row in data]
            execute_batch(cursor, insert_query, data_to_insert)

        postgres_connection.commit()
        print(f"Data loaded into PostgreSQL for table: {table_name}")

    except Exception as e:
        print(f"Error loading data into PostgreSQL: {str(e)}")

# Main ETL process
for table_info in tables_to_extract:
    table_name = table_info['obj']
    cdc_column = table_info['cdc_column']

    # Extract data from Oracle
    print(f"Extracting data from Oracle table: {table_name}")
    oracle_data = extract_from_oracle(table_name.upper())  # Ensure table name is in uppercase

    if oracle_data:
        # Load data into PostgreSQL
        load_into_postgres(table_name, oracle_data)
        print(f"Data loaded into PostgreSQL for table: {table_name}")

# record end time
end = time.time()

print("ETL process completed successfully.")
print("The time of execution of the program is:", (end - start) * 1000, "ms")

