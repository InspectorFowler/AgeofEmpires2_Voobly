import pandas as pd
import time

def sql_read(sql_path,db_conn):
    
    start = time.time()    
    query = open(sql_path, 'r')
    data = pd.DataFrame(pd.read_sql_query(query.read(), db_conn))
    print('Time taken to read from server : '+str(time.time() - start))

    return(data)