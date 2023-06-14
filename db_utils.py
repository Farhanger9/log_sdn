import os
import psycopg2
import db_config



table_format = """id SERIAL, \
player_name VARCHAR,\
end_time timestamp,\
duration INTEGER,\
ad_copy_name VARCHAR,\
num_of_screens INTEGER,\
campaign_name VARCHAR,\
frame_name VARCHAR,\
display_unit_name VARCHAR,\
impressions INTEGER,\
interactions INTEGER,\
extra_data VARCHAR, \
extra_data_id VARCHAR,\
extra_data_var VARCHAR,\
PRIMARY KEY (id)"""



def del_table(table_name):
    conn = psycopg2.connect(database=db_config.database,
                        user=db_config.user, password=db_config.password, 
                        host=db_config.host, port=db_config.port
    )

    conn.autocommit = True
    cursor = conn.cursor()
    sql_del = f'''DROP TABLE IF EXISTS {table_name.upper()};
    '''
    cursor.execute(sql_del)

    conn.commit()
    conn.close()

def create_tables(csvPaths:list, tableNames:list):

    if isinstance(csvPaths, list) and isinstance(tableNames, list):
        assert len(csvPaths) == len(tableNames), "The number of CSVs and tables must be same"
    elif isinstance(csvPaths, str) and isinstance(tableNames, str):
        csvPaths = [csvPaths]
        tableNames = [tableNames]
    else:
        return False, "CSV Paths and table names must be list"
    
    conn = psycopg2.connect(database=db_config.database,
                        user=db_config.user, password=db_config.password, 
                        host=db_config.host, port=db_config.port
    )

    conn.autocommit = True
    cursor = conn.cursor()

    def create_one_table(csv, table):
        
        # sql = f'''CREATE TABLE IF NOT EXISTS {table.upper()}({table_format});'''
        #
        # cursor.execute(sql)

        sql2 = f'''COPY {table}(player_name,end_time, duration, ad_copy_name, num_of_screens, campaign_name,frame_name,display_unit_name,impressions,interactions,extra_data, extra_data_id,extra_data_var)
FROM '{csv}'
DELIMITER ','
CSV HEADER;'''

        print(sql2)

        cursor.execute(sql2)
        
        sql3 = f'''select * from {table};'''
        cursor.execute(sql3)
        rows = cursor.fetchall()
        print(f"{table}:\t{len(rows)=}")
        # os.remove(csv)
    
    failed_list = []
    for csv_path, tablename in zip(csvPaths, tableNames):
        print(tablename,"===table")
        try:
            create_one_table(csv_path, tablename)
        except Exception as e:
            failed_list.append(tablename)
            print(repr(e))
            pass
    
    conn.commit()
    conn.close()
    if len(failed_list) != 0:
        return False, f"Table Names to be failed to create: {', '.join(failed_list)}"
    else:
        return True, "Successfully created tables"


def check_exists(table_name):
    import psycopg2

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=db_config.database,
                            user=db_config.user, password=db_config.password, 
                            host=db_config.host, port=db_config.port
    )

    cursor = conn.cursor()

    # Execute the query to check if the table exists
    sql_cmd = f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = '{table_name}')"
    cursor.execute(sql_cmd)

    # Fetch the result of the query
    exists = cursor.fetchone()[0]
    print(exists)

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return exists

def get_table_list():
    import psycopg2

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=db_config.database,
                            user=db_config.user, password=db_config.password, 
                            host=db_config.host, port=db_config.port
    )

    cursor = conn.cursor()

    # Execute the query to get a list of table names
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")

    # Fetch all the rows from the query result
    rows = cursor.fetchall()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    return [row[0] for row in rows]


def get_rows_from_table(table):

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(database=db_config.database,
                            user=db_config.user, password=db_config.password, 
                            host=db_config.host, port=db_config.port
    )

    cursor = conn.cursor()

    sql3 = f'''select * from {table.lower()};'''
    cursor.execute(sql3)
    rows = cursor.fetchall()
    print(f"{table}:\t{len(rows)=}")
    
    # Close the cursor and connection
    cursor.close()
    conn.close()

    return [row[0] for row in rows]
    

if __name__ == "__main__":
    # csv_path = "D:\\Workspace\\working\\Farhang-Work\\report\\log-report\\playlog.csv"

    # table_name = "DETAILS"
    # create_table(csv_path, table_name)
    tables_existed=['playlog20230429']
    for tab in tables_existed:
        # get_rows_from_table(tab)
        tab_exist = check_exists(tab.lower())
        print("{}: {}".format(tab, tab_exist))
        if tab_exist:
            del_table(tab.lower())

