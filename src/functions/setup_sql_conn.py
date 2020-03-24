import pyodbc
import pandas as pd
from sqlalchemy import create_engine

def setup_sql_conn(server, database):
    
    driver = '{SQL Server Native Client 11.0}'
    port = 1433

    db_conn = pyodbc.connect('DRIVER='+driver+
                             ';PORT='+str(port)+
                             ';SERVER='+server+
                             ';DATABASE='+database+
                             ';Trusted_Connection=yes')

    db_cursor = db_conn.cursor()

    engine = create_engine("mssql+pyodbc://"+server+"/"+database+"?driver=SQL+Server+Native+Client+11.0")
    return(db_conn,db_cursor,engine)

# fetch data from DB
def fetch_sql_data(query,db_conn):
    
    data = pd.DataFrame(pd.read_sql_query(query, db_conn))
    return(data)