import sqlite3

# create databse file
f = open("planes.db", "w")
f.close

db = sqlite3.connect("planes.db")
curs = db.cursor()	

# create airplanes table
curs.execute('''CREATE TABLE planes (
	plane_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	type VARCHAR(10) DEFAULT XXXXXXXXXX,
	model VARCHAR(10),
	se CHAR(1),
	me CHAR(1),
	sp CHAR(1),
	mp CHAR(1),
	jet CHAR(1),
	prop CHAR(1),
	pist CHAR(1)
	)''')

#f = open("planes.csv", "r")

#rows = f.readlines()
#for row in rows:
#	entries = row.strip().split(",")
#	if entries[4] != '\\N':
#		curs.execute("INSERT INTO airports (iata, icao, name, city, country, lat, long) VALUES(?, ?, ?, ?, ?, ?, ?)", (entries[4], entries[5], entries[1], entries[2], entries[3], entries[6], entries[7],))

db.commit()
db.close()
