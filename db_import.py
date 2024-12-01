# This file pulls from regulars.txt and imports it into SQLite when Docker runs
# Note: Docker will need to run this before the main app file

import sqlite3

#Read from regulars.txt
with open("regulars.txt", "r") as regulars:
    regulars_list = regulars.readlines()

# Connect to DB
db = sqlite3.connect('regulars.db')
c = db.cursor()

# Create the table
c.execute('''
    CREATE TABLE regulars(
    id INTEGER PRIMARY KEY,
    name TEXT,
    song TEXT)
''')
db.commit()

# Loop through the list and insert them into the table
for r in regulars_list:
    name, song = r.split("- ")
    entry = (name,song)
    c.execute('INSERT INTO regulars (name, song) VALUES (?,?)', entry)
    db.commit()

results = c.execute('SELECT * FROM regulars').fetchall()
c.close()
print(results)