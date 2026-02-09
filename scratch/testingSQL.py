import pandas as pd
import sqlite3

con = sqlite3.connect("WindTunnel.db")
query = """SELECT group_concat(name, '|') FROM pragma_table_info('TestDetailed');"""
df = pd.read_sql_query(query, con)
paramList = df.iloc[0,0].split("|")
print(paramList)
con.close()