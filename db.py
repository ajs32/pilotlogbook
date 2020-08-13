import sqlite3
from sqlite3 import Error

# Query DB for result
def db_query(db_name, q, params=None):
	db = sqlite3.connect(db_name)
	curs = db.cursor()	

	try:
		if params:
			curs.execute(q, params)
		else:
			curs.execute(q)
		qresult = curs.fetchall()
		db.close()
	except Error as e:
		return str(e)
	if type(qresult) == list:
		return qresult
	else: return None
	
# Query DB for JSON
def db_get_json(db_name, q, params=None):
	def dict_factory(curs, row):
		d = {}
		for idx, col in enumerate(curs.description):
			d[col[0]] = row[idx]
		return d

	db = sqlite3.connect(db_name)
	db.row_factory = dict_factory
	curs = db.cursor()

	try:
		if params:
			curs.execute(q, params)
		else:
			curs.execute(q)
		qresult = curs.fetchall()
		db.close()
	except Error as e:
		return str(e)
 	
	return qresult
	
# Initial Creation of user DB at registration
def create_user_db(user_id):
	# Create user DB
	db_name = user_id + ".db"
	db = open(db_name, 'w')
	db.close()
	
	# Connect DB and create cursor
	db = sqlite3.connect(db_name)
	curs = db.cursor()	
	# CReate tables FLIGHTS, PLANES, PILOTS and AIRPORTS
	curs.execute('''CREATE TABLE flights (
		id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		date DATE NOT NULL,
		flt_nr VARCHAR(10),
		dep INTEGER NOT NULL,
		dep_time TIMESTAMP NOT NULL,
		arr INTEGER NOT NULL,
		arr_time TIMESTAMP NOT NULL,
		reg INTEGER NOT NULL,
		tot_time INTEGER NOT NULL,
		pic INTEGER NOT NULL,
		fo INTEGER,
		pilot3 INTEGER,
		pilot4 INTEGER,
		pilot5 INTEGER,
		to_land CHAR(1),
		res1 TEXT,
		res2 TEXT,
		pic_time INTEGER,
		fo_time INTEGER,
		dual INTEGER,
		instructor INTEGER,
		examiner INTEGER,
		night INTEGER,
		ifr INTEGER,
		vfr INTEGER,
		deleted CHAR(1) DEFAULT N,
		FOREIGN KEY(dep) REFERENCES airports(ap_id),
		FOREIGN KEY(arr) REFERENCES airports(ap_id),
		FOREIGN KEY(reg) REFERENCES planes(plane_id),
		FOREIGN KEY(pic) REFERENCES pilots(pilot_id)
		FOREIGN KEY(fo) REFERENCES pilots(pilot_id),
		FOREIGN KEY(pilot3) REFERENCES pilots(pilot_id),
		FOREIGN KEY(pilot4) REFERENCES pilots(pilot_id),
		FOREIGN KEY(pilot5) REFERENCES pilots(pilot_id)
		)''')
	curs.execute('''CREATE TABLE planes (
		plane_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		tail VARCHAR(8) NOT NULL,
		type VARCHAR(10) DEFAULT XXXXXXXXXX,
		model VARCHAR(10),
		class VARCHAR(6) DEFAULT XXXXXX
		)''')
	curs.execute('''CREATE TABLE pilots (
		pilot_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		staff_nr VARCHAR(10),
		name TEXT NOT NULL,
		email TEXT,
		phone NUMERIC
		)''')
	curs.execute('''CREATE TABLE airports (
		ap_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
		iata CHAR(3) NOT NULL,
		icao CHAR(4) DEFAULT XXXX,
		name TEXT DEFAULT XXXXXXXXXX,
		city TEXT DEFAULT XXXXXXXXXX,
		country TEXT DEFAULT XXXXXXXXXX
		)''')
	curs.execute("CREATE TABLE settings (name TEXT, role VARCHAR(3))")

	db.commit()

# airports.csv is imported from https://openflights.org/data.html
	f = open("init_data/airports.csv", "r")
	rows = f.readlines()
	for row in rows:
		entries = row.strip().split(",")
		# import only airports with IATA codes avail
		if entries[4] != '\\N':
			curs.execute("INSERT INTO airports (iata, icao, name, city, country) VALUES(?, ?, ?, ?, ?)", (entries[4], entries[5], entries[1], entries[2], entries[3],))

	db.commit()
	db.close()

