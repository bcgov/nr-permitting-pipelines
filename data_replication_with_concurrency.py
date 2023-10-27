#!/usr/bin/env python
# coding: utf-8

# In[1]:
import psycopg2
import psycopg2.pool
import psycopg2.extras
import cx_Oracle
from psycopg2.extras import execute_batch
import configparser
import time
import json  # Import the json module
import concurrent.futures
from datetime import datetime
import sys

oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_12")

#mstr_schema=sys.argv[1]
#app_name=sys.argv[2]

mstr_schema='app_rrs1'
app_name='FTA'



start = time.time()

# Load the configuration file
#config = configparser.ConfigParser()
#config.read('C:/ODS/config_fta.ini')

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

#Concurrent tasks - number of tables to be replicated in parallel
concurrent_tasks = 5


# In[8]:


# Set up Oracle connection pool
dsn = cx_Oracle.makedsn(host=oracle_host, port=oracle_port, service_name=oracle_database)
OrcPool = cx_Oracle.SessionPool(user=oracle_username, password=oracle_password, dsn=dsn, min=concurrent_tasks,
                             max=concurrent_tasks, increment=1, encoding="UTF-8")
print(oracle_host, oracle_port, oracle_database, oracle_username, oracle_password)
print('Oracle Pool Successful')


# In[9]:


PgresPool = psycopg2.pool.ThreadedConnectionPool(
    minconn = concurrent_tasks, maxconn = concurrent_tasks,host=postgres_host, port=postgres_port, dbname=postgres_database, user=postgres_username, password=postgres_password
)
print('Postgres Connection Successful')


# In[10]:


def get_active_tables(mstr_schema,app_name):
  postgres_connection  = PgresPool.getconn()  
  postgres_cursor = postgres_connection.cursor()
  list_sql = f"""
  SELECT application_name,source_schema_name,source_table_name,target_schema_name,target_table_name,truncate_flag,cdc_flag,full_inc_flag,cdc_column,replication_order
  from {mstr_schema}.cdc_master_table_list c
  where  active_ind = 'Y' and application_name='{app_name}'
  order by replication_order, source_table_name
  """
  with postgres_connection.cursor() as curs:
            curs.execute(list_sql)
            rows = curs.fetchall()
  postgres_connection.commit()
  postgres_cursor.close()
  PgresPool.putconn(postgres_connection)
  return rows


# In[11]:


# Function to extract data from Oracle
def extract_from_oracle(table_name,source_schema):
    # Acquire a connection from the pool
    oracle_connection = OrcPool.acquire()
    oracle_cursor = oracle_connection.cursor()    
    try:
        # Use placeholders in the query and bind the table name as a parameter
        sql_query = f'SELECT * FROM {source_schema}.{table_name}'
        print(sql_query)
        oracle_cursor.execute(sql_query)
        rows = oracle_cursor.fetchall()
        OrcPool.release(oracle_connection)
        return rows
    except Exception as e:
        print(f"Error extracting data from Oracle: {str(e)}")
        OrcPool.release(oracle_connection)
        return []


# In[12]:


# Function to load data into PostgreSQL using execute_batch
def load_into_postgres(table_name, data,target_schema):
    postgres_connection = PgresPool.getconn()
    postgres_cursor = postgres_connection.cursor()
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
    except Exception as e:
        print(f"Error loading data into PostgreSQL: {str(e)}")
    finally:
        # Return the connection to the pool
        if postgres_connection:
            postgres_cursor.close()
            PgresPool.putconn(postgres_connection)
        


# In[13]:


def load_data_from_src_tgt(table_name,source_schema,target_schema):
        # Extract data from Oracle
        print(f'Source: Thread {table_name} started at ' + datetime.now().strftime("%H:%M:%S"))
        oracle_data = extract_from_oracle(table_name,source_schema)  # Ensure table name is in uppercase
        print(f'Source: Extraction for {table_name} completed at ' + datetime.now().strftime("%H:%M:%S"))
        
        if oracle_data:
            # Load data into PostgreSQL
            load_into_postgres(table_name, oracle_data, target_schema)
            print(f"Target: Data loaded into table: {table_name}")
            print(f'Target: Thread {table_name} ended at ' + datetime.now().strftime("%H:%M:%S"))


# In[14]:


if __name__ == '__main__':
    # Main ETL process
    #mstr_schema='app_rrs1'
    #app_name='FTA'
    active_tables_rows =get_active_tables(mstr_schema,app_name) 
    print(active_tables_rows)
    tables_to_extract = [(row[2],row[1],row[3]) for row in active_tables_rows]
    
    print(f"tables to extract are {tables_to_extract}")
    print(f'No of concurrent tasks:{concurrent_tasks}')
    # Using ThreadPoolExecutor to run tasks concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_tasks) as executor:
        # Submit tasks to the executor
        future_to_table = {executor.submit(load_data_from_src_tgt, table[0],table[1],table[2]): table for table in tables_to_extract}
        
        # Wait for all tasks to complete
        concurrent.futures.wait(future_to_table)
        
        # Print results
        for future in future_to_table:
            table_name = future_to_table[future]
            try:
                # Get the result of the task, if any
                future.result()
            except Exception as e:
                # Handle exceptions that occurred during the task
                print(f"Error replicating {table_name}: {e}")
    
    # record end time
    end = time.time()
    OrcPool.close()
    PgresPool.closeall()
    
    print("ETL process completed successfully.")
    print("The time of execution of the program is:", (end - start) , "secs")


# In[ ]:




