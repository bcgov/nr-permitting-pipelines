# Convert Oracle geometry to WKT: SDO_UTIL.TO_WKTGEOMETRY()
# Convert WKT to PostgreSQL: ST_GeomFromText()

import oracledb
import psycopg2
import os
import io
import time

# To-do: sort out which columns are necessary to replicate
# Pass these variables as config map: 
# schema = 'THE'
# table = 'HARVEST_AUTHORITY_GEOM'
# column = 'GEOMETRY'

# oracledb.init_oracle_client(lib_dir="/opt/oracle/instantclient_21_11")

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

# Set up Postgres database connection
postgres_connection = psycopg2.connect(user=postgres_username, password=postgres_password,
                                      host=postgres_host, port=postgres_port, database=postgres_database)

# Create Oracle cursor
oracle_cursor = oracle_connection.cursor()

# Create PostgreSQL cursor
postgres_cursor = postgres_connection.cursor()

# Query Oracle for geometry data and convert it to WKT
oracle_cursor.execute("SELECT SDO_UTIL.TO_WKTGEOMETRY(GEOMETRY) FROM THE.HARVEST_AUTHORITY_GEOM WHERE HARVEST_AUTHORITY_GEOM.HVA_SKEY = '52947'")

# Fetch all geometry data from Oracle
oracle_geometry_data = oracle_cursor.fetchall()

# Insert geometry data into PostgreSQL
for geometry_data in oracle_geometry_data:
    # Extract LOB geometry data from Oracle result
    oracle_geometry_clob = geometry_data[0]

    # Convert LOB to text
    oracle_geometry_wkt = oracle_geometry_clob.read()

    # Insert the geometry data into PostgreSQL
    postgres_cursor.execute("INSERT INTO geometry.harvest_authority_geom (geometry) VALUES (ST_GeomFromText(%s))", [oracle_geometry_wkt])

# Commit the changes and close the connections
postgres_connection.commit()

# record end time
end = time.time()

print("Geometry conversion completed successfully.")
print("The time of execution of the program is:", (end - start) * 1000, "ms")
