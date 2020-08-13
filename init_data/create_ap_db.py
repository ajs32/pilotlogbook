import sqlite3

# create databse file
f = open("airports.db", "w")
f.close

db = sqlite3.connect("airports.db")
curs = db.cursor()	

# create airports table
curs.execute('''CREATE TABLE airports (
	ap_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	iata CHAR(3) NOT NULL,
	icao CHAR(4) DEFAULT XXXX,
	name TEXT DEFAULT XXXXXXXXXX,
	city TEXT DEFAULT XXXXXXXXXX,
	country TEXT DEFAULT XXXXXXXXXX,
	lat	NUMERIC,
	long NUMERIC
	)''')

# Imported from https://openflights.org/data.html
f = open("airports.csv", "r")

rows = f.readlines()
for row in rows:
	entries = row.strip().split(",")
	if entries[4] != '\\N':
		curs.execute("INSERT INTO airports (iata, icao, name, city, country, lat, long) VALUES(?, ?, ?, ?, ?, ?, ?)", (entries[4], entries[5], entries[1], entries[2], entries[3], entries[6], entries[7],))

db.commit()
db.close()
