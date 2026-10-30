# setup_db.py
import pandas as pd
import sqlite3

print("Migrating CSV to SQLite Database...")

# 1. Read your existing data
df = pd.read_csv("data/conflict_data.csv")

# 2. Create and connect to a new SQLite database file
conn = sqlite3.connect("data/wildlife.db")

# 3. Write the data to a SQL table named 'incidents'
df.to_sql("incidents", conn, if_exists="replace", index=False)
conn.close()

print("✅ Success! Database created at data/wildlife.db")