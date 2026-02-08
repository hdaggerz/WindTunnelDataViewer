import pandas as pd
import sqlite3

con = sqlite3.connect("WindTunnel.db")
query = """SELECT DISTINCT RunId FROM TestDetailed;"""
df = pd.read_sql_query(query, con)
print(df['RunId'].tolist())
con.close()