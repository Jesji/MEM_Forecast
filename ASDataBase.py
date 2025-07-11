# database file
import pandas as pd
import zipfile
import glob
import os
from pathlib import Path
import sqlite3


# Function to get list of dfs for each zip file in download folder
def get_dfs_from_zips(download_folder):#give download folder
    zips_list = glob.glob(os.path.join(download_folder,"*.zip"))

    # list of df for each zipfile in donwloaded folder
    dfs_zip = list()
    for zip_path in zips_list:
        print(zip_path)
        # create object for the file
        with zipfile.ZipFile(zip_path) as z: 
            # dfs es la lista de df que se concatena en uno solo para cada zipfile
            dfs = [
                #read_csv_skipping_metadata(io.TextIOWrapper(z.open(file), encoding = 'utf-8').read())
                pd.read_csv(z.open(file),skiprows=7)
                for file in z.namelist() if "L0" in file
            ] 
        if dfs:
            #print(len(dfs))
            df_zip = pd.concat([df for df in dfs])
            df_zip.columns = [word.strip() for word in df_zip.columns]
            dfs_zip.append(df_zip)
        else:
            print("No L0 files in zip")
    return dfs_zip

def get_table_name(df,date_format ="%d/%m/%Y"):
    year = pd.to_datetime(min(df['Dia']), format=date_format).year
    return f"gen_{year}"

def create_df_table(download_folder,db_name = 'Generation.db'):
    os.remove(db_name)
    try:
        conn = sqlite3.connect(db_name) 
        print(f"Succesfull conection to recently created {db_name}")
        # get df from download_folder
        dfs_zip = get_dfs_from_zips(download_folder)
        tables_in_db = list()
        for df in dfs_zip:
            table_name = get_table_name(df)
            # save df to tables in DB
            tables_in_db.append(table_name)
            try:
                df.to_sql(table_name,conn, if_exists='replace', index=False)
                print(f'Table {table_name} was succesfully created in {db_name}')
            except:
                print('Error creating table {table_name}')
    except sqlite3.Error as e:
        print(f"{db_name} could not be created. Connection error {e}")
    finally:
        if conn:
            conn.close()
            print(f"Closed connection")     

def call_tables(db_name = 'Generation.db'):
    #print("Verificando los datos en la base de datos...")
    try:
        conn = sqlite3.connect(db_name)
        cursor= conn.cursor()
        res = cursor.execute("SELECT name FROM sqlite_master WHERE type ='table' ")
        tables = [row[0] for row in res.fetchall()]
        dfs = list()
        for table in tables:
            df = pd.read_sql(f"SELECT * FROM {table}",conn)
            dfs.append(df)
            #print(df)
    except sqlite3.Error as e:
        print(f"Error to connect to {db_name}. Error: {e}")
    finally:
        if conn:
            conn.close() 
    if dfs:
        print("Tables read succesfully")
    return dfs

