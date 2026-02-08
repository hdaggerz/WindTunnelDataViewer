import pandas as pd
import sqlite3
import matplotlib.pyplot as plt 

conn = sqlite3.connect("WindTunnel.db")
query = """SELECT * FROM TestDetailed WHERE RunId = 1 AND FrontRideHeight = 7.5;"""
df = pd.read_sql_query(query, conn)

print(df.head())

df['TotalDF'] = df['TotalDF'] * -1
plt.figure(figsize=(10,6))
plt.plot(df['RearRideHeight'], df['TotalDF'], marker='o')
plt.xlabel('Rear Ride Height (mm)')
plt.ylabel('Total Downforce (N)')
plt.title('Total Downforce vs Rear Ride Height')
plt.grid()
plt.show()