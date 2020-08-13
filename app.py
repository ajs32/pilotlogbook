import sqlite3
from sqlite3 import Error
import datetime
from datetime import date
from functions import escape, convert_to_minutes, convert_to_time, login_required, hash_password, verify_password
from db import create_user_db, db_query, db_get_json
import time, datetime

from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Get version information
with open("version.txt","r") as f:
	vers = f.readline().split()[1]

#------------------------------------------------------- /register
@app.route("/register", methods=["GET", "POST"])
def register():
	# Forget any user_id
	session.clear()

	if request.method == "POST":

		# Ensure username and password were typed in
		if not request.form.get("username") or not request.form.get("password") or not request.form.get("conf_password"):
			return render_template("register.html", msg="An error has occured during register")

		username = escape(request.form.get("username"))
		
		# Connect to DB and create a cursor
		db = sqlite3.connect("users.db")
		curs = db.cursor()

		# Query database for username
		try:
			curs.execute('SELECT * FROM users WHERE username=?', (username,))
		except Error as e:
			db.close()
			return render_template("register.html", msg=str(e), version = vers)
		rows = curs.fetchall()

		# Ensure username does not exist
		if len(rows) != 0:
			db.close()
			return render_template("register.html", msg="User with that username already exist", version = vers)
		# Ensure password matches confirmation
		if request.form.get("password") != request.form.get("conf_password"):
			db.close()
			return render_template("register.html", msg="Password does not match Password confirmation", version = vers)

		# HASH PASSWORD
		password = escape(request.form.get("password"))
		pass_hash = hash_password(password)

		# insert user credentials into USERS db
		try:
			curs.execute("BEGIN TRANSACTION")
			curs.execute("INSERT INTO users (username, hash) VALUES (?, ?)", (username, pass_hash,))
			db.commit()
		except Error:
			db.close()
			return render_template("register.html", msg="Unable to write to Database", version = vers)

		# get users unique ID
		try:
			curs.execute("SELECT id FROM users WHERE username=?", (username,))
		except Error:
			db.close()
			return render_template("register.html", msg=str(e), version = vers)
	
		# Get id number only. First items from first row [0][0]
		user_id = str(curs.fetchone()[0])
		db.close()
		
		# create logbook database
		create_user_db(user_id)

		# Redirect user to login page
		return render_template("login.html", msg="User created successfully", version = vers)

	# User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template("register.html", version = vers)


#------------------------------------------------------- /login
@app.route("/login", methods=["GET", "POST"])
def login():

	# Forget any user_id
	session.clear()

	# User reached route via POST (as by submitting a form via POST)
	if request.method == "POST":
		# Ensure username and password was submitted
		if not request.form.get("username") or not request.form.get("password"):
			return render_template("login.html", col="red", msg="An error has occured during login", version = vers)

		username = escape(request.form.get("username"))
		# Query database for username
		rows = db_query("users.db", "SELECT * FROM users WHERE username=?", (username,))

		# Good result is LIST, Error is STRING
		if type(rows) != list:
			return render_template("login.html", col="red", msg=rows, version = vers)
		
		# Ensure username exists and password is correct
		# [0] ID, [1] Name, [2] Hash
		password = escape(request.form.get("password"))
		if len(rows) != 1 or not verify_password(rows[0][2], password):
			return render_template("login.html", col="red", msg="Invalid username or password", version = vers)

		# Remember which user has logged in
		session["user_id"] = rows[0][0]
		session["key"] = -1

		# Redirect user to home page
		return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
	else:
		return render_template("login.html", version = vers)


#------------------------------------------------------- /logout
@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


#------------------------------------------------------- / FLIGHTS
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
	if request.method == "POST":
		todo = request.form.get("todo")
		key = request.form.get("key")

#		if not request.form.get("todo"):
		if todo == "add_flt" and session["key"] != key:
			session["key"] = key
#			return request.form.get("role")
			flt_data = []
			plane_id = None
			pic_id = None
			pilot_id = []		# ids of FO, and 3 pilots
			ap_ids = []			# ids of airports
			dep_ap_id = None
			arr_ap_id = None

			# Get all flt data into the list
			flt_data.append(escape(str(request.form.get("flt_nr")).upper()))							# 0 flt_nr
			flt_data.append(str(request.form.get("dep_ap")).upper())									# 1 dep_ap
			flt_data.append(str(request.form.get("arr_ap")).upper())									# 2 arr_ap
			flt_data.append(request.form.get("dep_date"))												# 3 dep_date
			flt_data.append(request.form.get("dep_date") + " " + request.form.get("dep_time") + ":00")	# 4 dep_time
			flt_data.append(request.form.get("arr_date") + " " + request.form.get("arr_time") + ":00")	# 5 arr_time
			flt_data.append(str(request.form.get("reg")).upper())										# 6 ac_reg
			flt_data.append(str(request.form.get("pic_name")).title())									# 7 pic
			if request.form.get("pf"):																	# 8 PF/PM
				flt_data.append('Y')
			else:
				flt_data.append('')
			flt_data.append(request.form.get("tot_time"))						# 9 tot_time

			flt_data.append(str(request.form.get("fo_name")).title())			# 10 fo_name
			flt_data.append(str(request.form.get("pilot3")).title())			# 11 pilot3
			flt_data.append(str(request.form.get("pilot4")).title())			# 12 pilot4
			flt_data.append(str(request.form.get("pilot5")).title())			# 13 pilot5

			flt_data.append(convert_to_minutes(str(request.form.get("pic_time"))))			# 14 pic_time
			flt_data.append(convert_to_minutes(str(request.form.get("fo_time"))))			# 15 fo_time
			flt_data.append(convert_to_minutes(str(request.form.get("dual_time"))))			# 16 dual time
			flt_data.append(convert_to_minutes(str(request.form.get("instr_time"))))		# 17 instructor
			flt_data.append(convert_to_minutes(str(request.form.get("exam_time"))))			# 18 examiner
			flt_data.append(convert_to_minutes(str(request.form.get("night_time"))))		# 19 night
			flt_data.append(convert_to_minutes(str(request.form.get("ifr_time"))))			# 20 IFR
			flt_data.append(convert_to_minutes(str(request.form.get("vfr_time"))))			# 21 VFR
			flt_data.append(str(request.form.get("remarks")))								# 22 Remarks


			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			# Check and insert IF new Plane
			try:
				curs.execute('SELECT plane_id FROM planes WHERE tail=?', (flt_data[6],))
				qresult = curs.fetchall()
				if len(qresult) == 0:
					curs.execute("INSERT INTO planes (tail) VALUES (?)", (flt_data[6],))
					curs.execute('SELECT plane_id FROM planes WHERE tail=?', (flt_data[6],))
					qresult = curs.fetchall()
					plane_id = qresult[0][0]
				else:
					plane_id = qresult[0][0]
			except Error:
				db.close()
				return render_template("flights.html", col="red", msg="Unable to process airplane data", version = vers)

			# Check and insert IF new Captain
			try:
				curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (flt_data[7],))
				qresult = curs.fetchall()
				if len(qresult) == 0:
					curs.execute('INSERT INTO pilots (name) VALUES (?)', (flt_data[7],))
					curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (flt_data[7],))
					qresult = curs.fetchall()
					pic_id = qresult[0][0]
				else:
					pic_id = qresult[0][0]
			except Error:
				db.close()
				return render_template("flights.html", col="red", msg="Unable to process PIC data", version = vers)

			# Check and insert IF new FO, Crew3, Crew4, Crew5
			for i in range(10,14):
				if flt_data[i] != '':
					try:
						curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (flt_data[i],))
						qresult = curs.fetchall()
						if len(qresult) == 0:
							curs.execute('INSERT INTO pilots (name) VALUES (?)', (flt_data[i],))
							curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (flt_data[i],))
							qresult = curs.fetchall()
							pilot_id.append(qresult[0][0])
						else:
							pilot_id.append(qresult[0][0])
					except Error:
						db.close()
						return render_template("flights.html", col="red", msg="Unable to assign pilot IDs", version = vers)
				else:
					pilot_id.append("")
				
			# Check and insert IF new Airport
			for i in range(1,3):
				try:
					curs.execute("SELECT ap_id FROM airports WHERE iata=?", (flt_data[i],))
					qresult = curs.fetchall()
					if len(qresult) == 0:
						curs.execute('INSERT INTO airports (iata) VALUES (?)', (flt_data[i],))
						curs.execute('SELECT ap_id FROM airports WHERE iata=?', (flt_data[i],))
						qresult = curs.fetchall()
						ap_ids.append(qresult[0][0])
					else:
						ap_ids.append(qresult[0][0])
				except Error:
					db.close()
					return render_template("flights.html", col="red", msg="Unable to assign airport IDs", version = vers)

			# insert all data into DB
			try:
				curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, 
						pic, fo, pilot3, pilot4, pilot5, to_land, pic_time, fo_time, dual, instructor, examiner, night,
						ifr, vfr, res1) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (flt_data[3], flt_data[0], ap_ids[0], flt_data[4], ap_ids[1], flt_data[5], plane_id, flt_data[9], pic_id, pilot_id[0], pilot_id[1], pilot_id[2], pilot_id[3], flt_data[8], flt_data[14], flt_data[15], flt_data[16], flt_data[17], flt_data[18], flt_data[19], flt_data[20], flt_data[21],flt_data[22],))
				# Save
				db.commit()
			except Error as e:
				db.close()
				return render_template("flights.html", col="red", msg=str(e), version = vers)

			# GEt new list of flight to display
			try:
				curs.execute('''SELECT date, flt_nr, ap1.iata, ap2.iata, tail, 
									((tot_time-tot_time%60)/60) || ':' || (tot_time%60),
									pic.name, to_land, id, fo.name, res1, 
									ap1.name, ap1.city, ap1.country,
									ap2.name, ap2.city, ap2.country, 
									type, model FROM flights
									JOIN airports AS ap1 ON flights.dep = ap1.ap_id
									JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
									JOIN planes ON flights.reg = planes.plane_id 
									LEFT JOIN pilots as pic ON flights.pic = pic.pilot_id 
									LEFT JOIN pilots as fo ON flights.fo = fo.pilot_id 
									WHERE flights.deleted="N" ORDER BY date DESC''')
			except Error as e:
				db.close()
				return render_template("flights.html", col="red", msg=str(e), version = vers)

			flt_list = curs.fetchall()

			db.close()
			return render_template("flights.html", msg="Flight added successfully", flt_data = flt_list, length = len(flt_list), version = vers)

		# Get Settings for AutoLog, role and name
		elif todo == "get_settings":
			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			qresult = db_query(db_name, "SELECT name, role from settings")

			# Good result is LIST, Error is STRING
			if type(qresult) == list:
				if len(qresult) != 0:
					return qresult[0][0] + "," + qresult[0][1]
				else:
					return "nil"
			else:
				return "nil"

		# If INVALID SUBMITION, no todo
		else:
			return render_template("error.html", msg = "Error has occured: Invalid submition", version = vers)

	else:		
		# Connect DB and create cursor
		db_name = str(session["user_id"]) + ".db"
#		DISPLAY FULL LIST OF FLIGHTS
		flt_list = db_query(db_name, '''SELECT date, flt_nr, ap1.iata, ap2.iata, tail, 
									((tot_time-tot_time%60)/60) || ':' || (tot_time%60),
									pic.name, to_land, id, fo.name, res1, 
									ap1.name, ap1.city, ap1.country,
									ap2.name, ap2.city, ap2.country, 
									type, model FROM flights
									JOIN airports AS ap1 ON flights.dep = ap1.ap_id
									JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
									JOIN planes ON flights.reg = planes.plane_id 
									LEFT JOIN pilots as pic ON flights.pic = pic.pilot_id 
									LEFT JOIN pilots as fo ON flights.fo = fo.pilot_id 
									WHERE flights.deleted="N" ORDER BY date DESC''')

		if type(flt_list) != list:
			return render_template("flights.html", col="red", msg=flt_list, version = vers)

		return render_template("flights.html", flt_data = flt_list, length = len(flt_list), version = vers)

#------------------------------------------------------- / TOTALS
@app.route("/totals")
@login_required
def totals():

	# Connect DB and create cursor
	db_name = str(session["user_id"]) + ".db"
	db = sqlite3.connect(db_name)
	curs = db.cursor()

	# get all SUMs of minutes
	try:
		curs.execute('''SELECT SUM(tot_time), SUM(pic_time), SUM(fo_time), 
						SUM(ifr), SUM(vfr),  SUM(night), 
						SUM(examiner),  SUM(instructor),  SUM(dual) FROM flights WHERE deleted="N" ''')
		qresult = curs.fetchone()
	except Error:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get totals from Database", version = vers)

	mejet = sejet = meprop = seprop = mepist = sepist = 0
	try:
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="MEJet" AND flights.deleted="N"')
		mejet = curs.fetchone()[0]
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="MEProp" AND flights.deleted="N"')
		meprop = curs.fetchone()[0]
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="MEPist" AND flights.deleted="N"')
		mepist = curs.fetchone()[0]
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="SEJet" AND flights.deleted="N"')
		sejet = curs.fetchone()[0]
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="SEProp" AND flights.deleted="N"')
		seprop = curs.fetchone()[0]
		curs.execute('SELECT SUM(tot_time) from flights JOIN planes AS planes_tbl ON reg=plane_id WHERE class="SEPist" AND flights.deleted="N"')
		sepist = curs.fetchone()[0]
	except Error as e:
		db.close()
		return render_template("totals.html", col="red", msg="Error: "+str(e)+"Unable to get ME/SE times from Database", version = vers)

	# convert minutes to TIME format
	tot_time_data = []
	for x in qresult:
		tot_time_data.append(convert_to_time(x))

	tot_time_data.append(convert_to_time(mejet))
	tot_time_data.append(convert_to_time(meprop))
	tot_time_data.append(convert_to_time(mepist))
	tot_time_data.append(convert_to_time(sejet))
	tot_time_data.append(convert_to_time(seprop))
	tot_time_data.append(convert_to_time(sepist))

	# Get all different aiplane types from DB
	try:
		curs.execute("SELECT DISTINCT type FROM planes")
		pl_types = curs.fetchall()
	except Error:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get Plane Types from DB", flt_data = tot_time_data, version = vers)		

	times_on_type = []
	try:
		for pl_type in pl_types:
			curs.execute('''SELECT SUM(tot_time), SUM(pic_time), SUM(fo_time) from flights
							JOIN planes ON reg=plane_id WHERE type=? AND flights.deleted="N" ''', (pl_type[0],))
			tmp_lst = []
			tmp_lst.append(pl_type[0])

			qresult = curs.fetchone()
			for x in qresult:
				tmp_lst.append(convert_to_time(x))

			times_on_type.append(tmp_lst)

	except Error:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to calculate times for airplane types", flt_data = tot_time_data, version = vers)

	# Get landing currency date
	cur_data = []
	try:
		curs.execute('SELECT date from flights WHERE deleted="N" AND to_land="Y" ORDER BY date DESC LIMIT 3')
		qresult = curs.fetchall()
		if len(qresult) > 2:
			cur_data.append(qresult[2][0])
	except Error:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get dates for landing currency", flt_data = tot_time_data, version = vers)
	
	# Get accumulated times and landing currency
	currDate=date.today()
	# 30 dyas
	y = currDate - datetime.timedelta(30)
	try:
		curs.execute('''SELECT SUM(tot_time) from flights WHERE date > ? AND deleted="N"''', (y,))
		cur_data.append(convert_to_time(curs.fetchone()[0]))
	except Error as e:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get 30 days flight time", flt_data = tot_time_data, version = vers)
	# 90 days
	y = currDate - datetime.timedelta(90)
	try:
		curs.execute('''SELECT SUM(tot_time) from flights WHERE date > ? AND deleted="N"''', (y,))
		cur_data.append(convert_to_time(curs.fetchone()[0]))
	except Error as e:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get 90 days flight time", flt_data = tot_time_data, version = vers)
	# 6 months
	y = currDate - datetime.timedelta(182)
	try:
		curs.execute('''SELECT SUM(tot_time) from flights WHERE date > ? AND deleted="N"''', (y,))
		cur_data.append(convert_to_time(curs.fetchone()[0]))
	except Error as e:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get 6 months flight time", flt_data = tot_time_data, version = vers)
	# 1 year
	y = currDate - datetime.timedelta(365)
	try:
		curs.execute('''SELECT SUM(tot_time) from flights WHERE date > ? AND deleted="N"''', (y,))
		cur_data.append(convert_to_time(curs.fetchone()[0]))
	except Error as e:
		db.close()
		return render_template("totals.html", col="red", msg="Unable to get 1 year flight time", flt_data = tot_time_data, version = vers)

	db.close()
	return render_template("totals.html", flt_data = tot_time_data, type_data = times_on_type, cur_data =cur_data, version = vers)

#------------------------------------------------------- / PLANES
@app.route("/planes", methods=["GET", "POST"])
@login_required
def planes():
	if request.method == "POST":
		if  str(request.form.get("todo")) == "add" or str(request.form.get("todo")) == "update":
			# if key is not valid, return error or assign new key
			if session["key"] == request.form.get("key"):
				return render_template("error.html", msg = "Error has occured: Invalid submition", version = vers)
			else: session["key"] = request.form.get("key")

			# Get plane data into list
			pln_data = []
			pln_data.append(str(request.form.get("tail")).upper())
			pln_data.append(str(request.form.get("type")).upper())
			pln_data.append(str(request.form.get("model")).upper())
			pln_data.append(str(request.form.get("class")))			
			pln_data.append(str(request.form.get("pln_id")))			

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			if request.form.get("todo") == "add":
				# search for subbmitted plain tail
				try:
					curs.execute('SELECT * FROM planes WHERE tail=?', (pln_data[0],))
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("planes.html", lbl="Add new aircraft", col="red", msg=str(e), version = vers)

				if len(qresult) == 0:	
					# if such tail does not exist, add to DB and report success
					try:
						curs.execute('''INSERT INTO planes (tail, type, model, class)
									VALUES (?, ?, ?, ?)''', (pln_data[0], pln_data[1], pln_data[2], pln_data[3],))
						db.commit()
					except Error as e:
						db.close()
						return render_template("planes.html", lbl="Add new aircraft", col="red", msg=str(e), version = vers)

					try:
						curs.execute('SELECT tail, type, model, class, plane_id FROM planes ORDER BY tail')
						plane_list = curs.fetchall()
					except Error:
						db.close()
						return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane list", version = vers)

					db.close()
					return render_template("planes.html", msg="New aircraft added successfully", plane_list = plane_list, length=len(plane_list), version = vers)
				else:
					# if tail EXIST, close DB and report PLANE EXIST in DB
					try:
						curs.execute('SELECT tail, type, model, class, plane_id FROM planes ORDER BY tail')
						plane_list = curs.fetchall()
					except Error:
						db.close()
						return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane list", version = vers)

					db.close()
					return render_template("planes.html", lbl="Add new aircreft", col="red", msg="Aircraft with such registration already exist", plane_list = plane_list, length=len(plane_list), version = vers)


			else:
				# if Call is to update information
				try:
					curs.execute('''UPDATE planes SET tail=?, type=?, model=?, class=? WHERE plane_id=?
								''', (pln_data[0], pln_data[1], pln_data[2], pln_data[3], pln_data[4],))
					db.commit()
				except Error:
					db.close()
					return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to update airplane info", version = vers)

				try:
					curs.execute('SELECT tail, type, model, class, plane_id FROM planes ORDER BY tail')
					plane_list = curs.fetchall()
				except Error:
					db.close()
					return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane list", version = vers)

				db.close()
				return render_template("planes.html", lbl="Add new aircraft", msg="Aircraft information updated successfully", plane_list = plane_list, length=len(plane_list), version = vers)

		else:
			# If edit button pressed
			plane_id = request.form.get("pln_id")

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			# search for subbmitted plain tail
			try:
				curs.execute('SELECT * FROM planes WHERE plane_id=?', (plane_id,))
				plane_data = curs.fetchone()
			except Error:
				db.close()
				return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane data", version = vers)
			try:
				curs.execute('SELECT tail, type, model, class, plane_id FROM planes ORDER BY tail')
				plane_list = curs.fetchall()
			except Error:
				db.close()
				return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane list", version = vers)

			db.close()		
			return render_template("planes.html", lbl="Update aircraft information", plane_data = plane_data, plane_list = plane_list, length=len(plane_list), version = vers)

	else:
		# Connect DB and create cursor
		db_name = str(session["user_id"]) + ".db"
		plane_list = db_query(db_name, 'SELECT tail, type, model, class, plane_id FROM planes ORDER BY tail')

		if type(plane_list) != list:
			return render_template("planes.html", lbl="Add new aircraft", col="red", msg="Unable to get airplane list", version = vers)

		return render_template("planes.html", lbl="Add new aircraft", plane_list = plane_list, length=len(plane_list), version = vers)


#------------------------------------------------------- / PILOTS
@app.route("/pilots", methods=["GET", "POST"])
@login_required
def pilots():
	if request.method == "POST":
		if str(request.form.get("todo")) == "add" or str(request.form.get("todo")) == "update":

			# if key is not valid, return error or assign new key
			if session["key"] == request.form.get("key"):
				return render_template("error.html", msg = "Error has occured: Invalid submition", version = vers)
			else: session["key"] = request.form.get("key")

			# Get plane data into list
			pil_data = []
			pil_data.append(str(request.form.get("staff_nr")).upper())
			pil_data.append(str(request.form.get("name")).title())
			pil_data.append(str(request.form.get("email")))
			pil_data.append(str(request.form.get("phone")))
			pil_data.append(str(request.form.get("pil_id")))			

#			return render_template("test.html", test_data=pil_data)

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			if request.form.get("todo") == "add":
				try:
					# search for subbmitted plain tail
					curs.execute('SELECT * FROM pilots WHERE name=?', (pil_data[1],))
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("pilots.html", lbl="Add new pilot", col="red", msg=str(e), version = vers)

				if len(qresult) == 0:
					# if such tail does not exist, add to DB and report success
					try:
						curs.execute('''INSERT INTO pilots (staff_nr, name, email, phone)
									VALUES (?, ?, ?, ?)''', (pil_data[0], pil_data[1], pil_data[2], pil_data[3],))
						db.commit()
					except Error:
						db.close()
						return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to insert pilot data into Database", version = vers)

					try:
						curs.execute('SELECT name, staff_nr, email, phone, pilot_id FROM pilots ORDER BY name')
						pilot_list = curs.fetchall()
					except Error:
						db.close()
						return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot list", version = vers)

					db.close()
					return render_template("pilots.html", lbl="Add new pilot", msg="New pilot added successfully", pilot_list = pilot_list, length=len(pilot_list), version = vers)

				else:
					# if tail EXIST, close DB and report PILOT EXIST in DB
					try:
						curs.execute('SELECT name, staff_nr, email, phone, pilot_id FROM pilots ORDER BY name')
						pilot_list = curs.fetchall()
					except Error:
						db.close()
						return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot list", version = vers)

					db.close()
					return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Pilot with such name already exist", pilot_list = pilot_list, length=len(pilot_list), version = vers)

			else:
				# if Call is to update information
				try:
					curs.execute('''UPDATE pilots SET staff_nr=?, name=?, email=?, phone=? WHERE pilot_id=?
								''', (pil_data[0], pil_data[1], pil_data[2], pil_data[3], pil_data[4],))
					db.commit()
				except Error:
					db.close()
					return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to update pilot data", version = vers)

				try:
					curs.execute('SELECT name, staff_nr, email, phone, pilot_id FROM pilots ORDER BY name')
					pilot_list = curs.fetchall()
				except Error:
					db.close()
					return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot list", version = vers)

				db.close()
				return render_template("pilots.html", lbl="Add new pilot", msg="Information updated successfully", pilot_list = pilot_list, length=len(pilot_list), version = vers)

		else:
	# If edit button pressed
			pilot_id = request.form.get("pil_id")

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			# search for subbmitted plain tail
			try:
				curs.execute('SELECT * FROM pilots WHERE pilot_id=?', (pilot_id,))
				pilot_data = curs.fetchone()
			except Error:
				db.close()
				return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot data", version = vers)

			try:
				curs.execute('SELECT name, staff_nr, email, phone, pilot_id FROM pilots ORDER BY name')
				pilot_list = curs.fetchall()
			except Error:
				db.close()
				return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot list", version = vers)

			db.close()
			return render_template("pilots.html", lbl="Update pilot information", pilot_data = pilot_data, pilot_list = pilot_list, length=len(pilot_list), version = vers)

	else:
		# Connect DB and create cursor
		db_name = str(session["user_id"]) + ".db"
		pilot_list = db_query(db_name, 'SELECT name, staff_nr, email, phone, pilot_id FROM pilots ORDER BY name')

		if type(pilot_list) != list:
			return render_template("pilots.html", lbl="Add new pilot", col="red", msg="Unable to get pilot list", version = vers)

		return render_template("pilots.html", lbl="Add new pilot", pilot_list = pilot_list, length=len(pilot_list), version = vers)


#------------------------------------------------------- / AIRPORTS
@app.route("/airports", methods=["GET", "POST"])
@login_required
def airports():
	if request.method == "POST":

		todo = request.form.get("todo")

		# Get airport requested information
		if todo == "lookup":
			qrequest = []
			req_str = ""

			if not request.form.get("iata"): pass
			else: 
				qrequest.append(request.form.get("iata").upper())
				req_str += " iata=?"
			if not request.form.get("icao"): pass
			else: 
				if len(req_str) != 0:
					req_str += "AND"
				qrequest.append(request.form.get("icao").upper())
				req_str += " icao=?"
			if not request.form.get("name"): pass
			else: 
				if len(req_str) != 0:
					req_str += "AND"
				qrequest.append(request.form.get("name").title())
				req_str += " name=?"
			if not request.form.get("city"): pass
			else: 
				if len(req_str) != 0:
					req_str += "AND"
				qrequest.append(request.form.get("city").capitalize())
				req_str += " city=?"
			if not request.form.get("country"): pass
			else: 
				if len(req_str) != 0:
					req_str += "AND"
				qrequest.append(request.form.get("country").title())
				req_str += " country=?"

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			qresult = db_query(db_name, 'SELECT name, iata, icao, city, country FROM airports WHERE' + req_str, qrequest)

			if type(qresult) != list:
				return "Error: " + qresult

			if len(qresult) != 0:
				return str(len(qresult))+str(qresult)
			else: return "EAirport with such information was not found"
		
		# Display requested airport information
		elif todo == "display":
			db_name = str(session["user_id"]) + ".db"
			qresult = db_query(db_name, 'SELECT iata, icao, name, city, country FROM airports WHERE ap_id=?', (request.form.get("ap_id"),))

			if type(qresult) != list:
				return "Error: " + qresult

			return str(qresult)

		# Update airport information
		elif todo == "update":
			
			ap_id = request.form.get("ap_id")
			ap_iata = request.form.get("upd_iata").upper()
			ap_icao = request.form.get("upd_icao").upper()
			ap_name = request.form.get("upd_name").title()
			ap_city = request.form.get("upd_city").capitalize()
			ap_country = request.form.get("upd_country").capitalize()


			db_name = str(session["user_id"]) + ".db"
			qresult = db_query(db_name, '''UPDATE airports SET iata=?, icao=?, name=?, city=?, country=? 
										WHERE ap_id=?''', (ap_iata, ap_icao, ap_name, ap_city, ap_country, ap_id,))

			if type(qresult) != list:
				return "Error: " + qresult

			return redirect("/airports")

		else:
			return render_template("airports.html", col="red", msg="Error has occured: Invalid submition", version = vers)

	# GET method
	else:
		db_name = str(session["user_id"]) + ".db"
		ap_list = db_query(db_name, '''SELECT name, iata, icao, city, country, ap_id FROM airports WHERE 
									name="XXXXXXXXXX" or icao="XXXX" or city="XXXXXXXXXX" or country="XXXXXXXXXX" ''')

		if type(ap_list) != list:
			return render_template("airports.html", col="red", msg="Unable to get airport list", version = vers)

		# AIRPORT XXX is present in DB and will return from DB
		if len(ap_list) != 0 and len(ap_list) != 1:
			return render_template("airports.html", ap_list = ap_list, length = len(ap_list), version = vers)
		else:
			return render_template("airports.html", version = vers)

#------------------------------------------------------- / AllAirports
@app.route("/allairports")
@login_required
def allairports():

	# Connect DB and create cursor
	db_name = str(session["user_id"]) + ".db"
	qresult = db_query(db_name, 'SELECT name, iata, icao, city, country FROM airports')

	if type(qresult) != list:
		return render_template("allairports.html", col="red", msg="Unable to get airport list", version = vers)
	
	return render_template("allairports.html", msg="Full list of Airports", ap_list=qresult, version = vers)

#------------------------------------------------------- / editFlight
@app.route("/editflight", methods=["GET", "POST"])
@login_required
def allflights():

	if request.method == "POST":
#		IF POST WITH DELETE, DELETE PARTICULAR FLIGHT FROM DB
		if request.form.get("todo") == "delete":

			flt_id = str(request.form.get("flt_id"))

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			try:
				curs.execute("UPDATE flights SET deleted='Y' WHERE id=?", (flt_id,))
				db.commit()
			except Error:
				db.close()
				return render_template("error.html", msg = "Unable to delete the flight", version = vers)

			try:	
				curs.execute('''SELECT date, flt_nr, ap1.iata, ap2.iata, tail, 
									((tot_time-tot_time%60)/60) || ':' || (tot_time%60),
									pic.name, to_land, id, fo.name, res1, 
									ap1.name, ap1.city, ap1.country,
									ap2.name, ap2.city, ap2.country, 
									type, model FROM flights
									JOIN airports AS ap1 ON flights.dep = ap1.ap_id
									JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
									JOIN planes ON flights.reg = planes.plane_id 
									LEFT JOIN pilots as pic ON flights.pic = pic.pilot_id 
									LEFT JOIN pilots as fo ON flights.fo = fo.pilot_id 
									WHERE flights.deleted="N" ORDER BY date DESC''')

				flt_list = curs.fetchall()
			except Error:
				db.close()
				return render_template("error.html", msg = "Unable to get flights list", version = vers)

			db.close()
			return render_template("flights.html", msg = "Flight was deleted successfully", flt_data = flt_list, length = len(flt_list), version = vers)

#		IF POST WITH SAVE, UPDATE INFO FOR PARTICULAR FLIGHT IN DB
		elif request.form.get("todo") == "save":
			# Get all flt data
			apts = []
			pilots = []
			ap_ids = []
			pilots_ids = []

			flt_id = int(request.form.get("flt_id"))
			date = str(request.form.get("date"))
			flt_nr = str(request.form.get("flt_nr")).upper()
			tail = str(request.form.get("reg")).upper()
			apts.append(str(request.form.get("dep_ap")).upper())
			apts.append(str(request.form.get("arr_ap")).upper())
			dep_date = str(request.form.get("dep_time"))
			arr_date = str(request.form.get("arr_time"))
			tot_time = str(request.form.get("tot_time"))
			if request.form.get("pf"):
				pf='Y'
			else:
				pf=""
			pilots.append(str(request.form.get("pic_name")).title())
			pilots.append(str(request.form.get("fo_name")).title())
			pilots.append(str(request.form.get("crew3")).title())
			pilots.append(str(request.form.get("crew4")).title())
			pilots.append(str(request.form.get("crew5")).title())
			pic_time = convert_to_minutes(str(request.form.get("pic_time")))
			fo_time = convert_to_minutes(str(request.form.get("fo_time")))
			night = convert_to_minutes(str(request.form.get("night")))
			ifr = convert_to_minutes(str(request.form.get("ifr")))
			vfr = convert_to_minutes(str(request.form.get("vfr")))
			instr = convert_to_minutes(str(request.form.get("instr")))
			exam = convert_to_minutes(str(request.form.get("exam")))
			dual = convert_to_minutes(str(request.form.get("dual")))
	

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			# Check and insert IF new Plane
			try:
				curs.execute('SELECT plane_id FROM planes WHERE tail=?', (tail,))
				qresult = curs.fetchall()
			except Error as e:
				db.close()
				return render_template("error.html", msg=str(e), version = vers)

			if len(qresult) == 0:
				try:
					curs.execute("INSERT INTO planes (tail) VALUES (?)", (tail,))
					curs.execute('SELECT plane_id FROM planes WHERE tail=?', (tail,))
					qresult = curs.fetchall()
					plane_id = qresult[0][0]
				except Error:
					db.close()
					return render_template("error.html", msg="Unable to get airplane ID", version = vers)
			else:
				plane_id = qresult[0][0]

			# Check and insert IF new Pilot
			for pilot in pilots:
				if pilot != 'None' and pilot != "":
					try:
						curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (pilot,))
						qresult = curs.fetchall()
					except Error as e:
						db.close()
						return render_template("error.html", msg=str(e), version = vers)

					if len(qresult) == 0:
						try:
							curs.execute('INSERT INTO pilots (name) VALUES (?)', (pilot,))
							curs.execute('SELECT pilot_id FROM pilots WHERE name=?', (pilot,))
							qresult = curs.fetchall()
							pilots_ids.append(qresult[0][0])
						except Error:
							db.close()
							return render_template("error.html", msg="Unable to get pilot IDs", version = vers)
					else:
						pilots_ids.append(qresult[0][0])
				else:
					pilots_ids.append("")
				
			# Check and insert IF new Airport
			for apt in apts:
				try:
					curs.execute("SELECT ap_id FROM airports WHERE iata=?", (apt,))
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("error.html", msg=str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute('INSERT INTO airports (iata) VALUES (?)', (apt,))
						curs.execute('SELECT ap_id FROM airports WHERE iata=?', (apt,))
						qresult = curs.fetchall()
						ap_ids.append(qresult[0][0])
					except Error:
						db.close()
						return render_template("error.html", msg="Unable to get airport IDs", version = vers)
				else:
					ap_ids.append(qresult[0][0])

			# update data all data into DB
			try:
				curs.execute('''UPDATE flights SET date=?, flt_nr=?, dep=?, dep_time=?, arr=?, arr_time=?, reg=?, tot_time=?, 
						pic=?, fo=?, pilot3=?, pilot4=?, pilot5=?, to_land=?, pic_time=?, fo_time=?, dual=?, instructor=?, examiner=?,
						night=?, ifr=?, vfr=? WHERE id=?''', (date, flt_nr, ap_ids[0], dep_date, ap_ids[1], arr_date, plane_id, tot_time, pilots_ids[0], pilots_ids[1], pilots_ids[2], pilots_ids[3], pilots_ids[4], pf, pic_time, fo_time, dual, instr, exam, night, ifr, vfr, flt_id,))
				# Save
				db.commit()
			except Error:
				db.close()
				return render_template("error.html", msg="Unable to update flight data", version = vers)
			
			try:
				curs.execute('''SELECT date, flt_nr, ap1.iata, ap2.iata, tail, 
									((tot_time-tot_time%60)/60) || ':' || (tot_time%60),
									pic.name, to_land, id, fo.name, res1, 
									ap1.name, ap1.city, ap1.country,
									ap2.name, ap2.city, ap2.country, 
									type, model FROM flights
									JOIN airports AS ap1 ON flights.dep = ap1.ap_id
									JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
									JOIN planes ON flights.reg = planes.plane_id 
									LEFT JOIN pilots as pic ON flights.pic = pic.pilot_id 
									LEFT JOIN pilots as fo ON flights.fo = fo.pilot_id 
									WHERE flights.deleted="N" ORDER BY date DESC''')

				flt_list = curs.fetchall()
			except Error:
				db.close()
				return render_template("error.html", msg="Unable to get flights list", version = vers)

			db.close()
			return render_template("flights.html", msg = "Information updated successfully", flt_data = flt_list, length = len(flt_list), version = vers)

		else:
#		IF JUST 'POST', DISPLAY FULL INFORMATION ABOUT PARTICULAR FLIGHT TO EDIT
			flt_id = request.form.get("flt_id")

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			flt_data = db_query(db_name, '''SELECT date, flt_nr, ap1.iata, dep_time, ap2.iata, arr_time, tail, pic.name,
					fo.name, to_land,  crew3.name, crew4.name, crew5.name,
					((pic_time-pic_time%60)/60) || ':' || (pic_time%60), ((fo_time-fo_time%60)/60) || ':' || (fo_time%60),
					((dual-dual%60)/60) || ':' || (dual%60), ((instructor-instructor%60)/60) || ':' || (instructor%60),
					((examiner-examiner%60)/60) || ':' || (examiner%60), ((night-night%60)/60) || ':' || (night%60),
					((ifr-ifr%60)/60) || ':' || (ifr%60), ((vfr-vfr%60)/60) || ':' || (vfr%60) FROM flights
					JOIN airports AS ap1 ON flights.dep = ap1.ap_id
					JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
					JOIN planes ON flights.reg = planes.plane_id 
					LEFT JOIN pilots AS pic ON flights.pic = pic.pilot_id 
					LEFT JOIN pilots AS fo ON flights.fo = fo.pilot_id 
					LEFT JOIN pilots AS crew3 ON flights.pilot3 = crew3.pilot_id 
					LEFT JOIN pilots AS crew4 ON flights.pilot3 = crew4.pilot_id 
					LEFT JOIN pilots AS crew5 ON flights.pilot3 = crew5.pilot_id
					WHERE id=?''', (flt_id,))

			if type(flt_data) != list:
				return render_template("error.html", msg="Unable to get flight data", version = vers)

			return render_template("editflight.html", msg="Edit Flight", flt_id=flt_id, flt_data=flt_data[0], version = vers)

	else:
#		DISPLAY FULL LIST OF FLIGHTS
		redirect("/")


#------------------------------------------------------- / PRINT
@app.route("/print", methods=["GET", "POST"])
@login_required
def print():
	if request.method == "POST":
		if request.form.get("todo") == "logbook":
			db_name = str(session["user_id"]) + ".db"
			try:
				flights = db_get_json(db_name, '''SELECT date, ap1.iata AS iata1, dep_time, ap2.iata AS iata2, arr_time, type, tail,
											tot_time, pic.name, to_land, pic_time, fo_time, ifr, night, dual,
											instructor, examiner, res1 FROM flights
											JOIN airports AS ap1 ON flights.dep = ap1.ap_id
											JOIN airports AS ap2 ON flights.arr = ap2.ap_id 
											JOIN planes ON flights.reg = planes.plane_id 
											LEFT JOIN pilots AS pic ON flights.pic = pic.pilot_id 
											WHERE flights.deleted="N" AND flt_nr!="PREVEXP" ORDER BY date''')
			except Error as e:
				return "Error: " + str(e)	

			return str(flights).replace("'", '"')

		else:
			return "Error, invalid request" 
	else:
		return render_template("print.html", version = vers)
			

#------------------------------------------------------- / SETTINGS
@app.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
	if request.method == "POST":
		todo = request.form.get("todo")
#!!!!!!!!!!!!!!!!!!SETTINGS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		if todo == "settings":
			role = request.form.get("role").upper()
			name = request.form.get("name").title()
			if role.isalpha() != True:
				return "Error: Invalid role"

			for i in range(len(name)):
				if name[i].isalpha() != True and name[i] != " ":
					return "Error: Invalid name"
				else: continue

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			try:
				curs.execute("SELECT * from settings")
				qresult = curs.fetchall()
			except Error as e:
				db.close()
				return "Error: " + str(e)

			if len(qresult) != 0:
				try:
					curs.execute("UPDATE settings SET name=?, role=?", (name, role,))
					db.commit()
				except Error:
					db.close()
					return "Error: Unable to update settings"
			else:
				try:
					curs.execute("INSERT INTO settings (name, role) VALUES (?, ?)", (name, role,))
					db.commit()
				except Error:
					db.close()
					return "Error: Unable to update settings"

			return "Settings saved successfully (" + role + " " + name + ")"

#!!!!!!!!!!!!!!!!!!PASSWORD!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		elif todo == "password":
			# Check entries
			if request.form.get("old_pass") == "":
				return "Error: Old password is missing"
			elif request.form.get("new_pass") != request.form.get("conf_new_pass"):
				return "Error: New password does not match confirmation"

			# Connect DB and create cursor
			db = sqlite3.connect("users.db")
			curs = db.cursor()

			# Query database for username
			try:
				curs.execute("SELECT * FROM users WHERE id=?", str(session['user_id']))
				rows = curs.fetchall()
			except Error as e:
				db.close()
				return "Error: " + str(e)				

			# check password
			old_pass = escape(request.form.get("old_pass"))

			if len(rows) != 1 or not verify_password(rows[0][2], old_pass):
				db.close()
				return "Error: Wrong password provided"

			# hash new pass, update user DB and return settings
			new_pass = escape(request.form.get("new_pass"))
			pass_hash = hash_password(new_pass)

			try:
				curs.execute("UPDATE users SET hash=? WHERE id=?", (pass_hash, str(session['user_id']),))
			except Error:
				db.close()
				return "Error: unable to change password"

			db.commit()
			db.close()
			return "Password changed successfully"

#!!!!!!!!!!!!!!!!!!PREVEXP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		elif todo == "prevexp":
			# if key is not valid, return error or assign new key
			if session["key"] == request.form.get("key"):
				return render_template("error.html", msg = "Error has occured: Invalid submition", version = vers)
			else: session["key"] = request.form.get("key")

#			return "Success"

			pic_time = convert_to_minutes(request.form.get("pic_time"))
			fo_time = convert_to_minutes(request.form.get("fo_time"))
			mejet = convert_to_minutes(request.form.get("me_fan"))
			meprop = convert_to_minutes(request.form.get("me_prop"))
			mepist = convert_to_minutes(request.form.get("me_pist"))
			sejet = convert_to_minutes(request.form.get("se_fan"))
			seprop = convert_to_minutes(request.form.get("se_prop"))
			sepist = convert_to_minutes(request.form.get("se_pist"))
			ifr = convert_to_minutes(request.form.get("ifr"))
			vfr = convert_to_minutes(request.form.get("vfr"))
			night = convert_to_minutes(request.form.get("night"))
			exam = convert_to_minutes(request.form.get("exam"))
			instr = convert_to_minutes(request.form.get("instr"))
			dual = convert_to_minutes(request.form.get("dual"))

			tot_time = pic_time + fo_time + exam + instr + dual - mejet - meprop - mepist - sejet - seprop - sepist
			if tot_time < 0: 
				tot_time = 0

			# Connect DB and create cursor
			db_name = str(session["user_id"]) + ".db"
			db = sqlite3.connect(db_name)
			curs = db.cursor()

			# Check PREV EXP plane X
			try:
				curs.execute("SELECT plane_id FROM planes WHERE tail='XXX'")
				qresult = curs.fetchall()
			except Error as e:
				db.close()
				return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

			if len(qresult) == 0:
				try:
					curs.execute("INSERT INTO planes (tail) VALUES ('XXX')")
					curs.execute("SELECT plane_id FROM planes WHERE tail='XXX'")
					qresult = curs.fetchall()
					plane_id = qresult[0][0]
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to get aiplane ID", version = vers)
			else:
				plane_id = qresult[0][0]

			# Check PREV EXP pilot X
			try:
				curs.execute("SELECT pilot_id FROM pilots WHERE name='XXX'")
				qresult = curs.fetchall()
			except Error as e:
				db.close()
				return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

			if len(qresult) == 0:
				try:
					curs.execute("INSERT INTO pilots (name) VALUES ('XXX')")
					curs.execute("SELECT pilot_id FROM pilots WHERE name='XXX'")
					qresult = curs.fetchall()
					pic_id = qresult[0][0]
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to get pilot ID", version = vers)
			else:
				pic_id = qresult[0][0]
				
			# Check PREV EXP airport X
			try:
				curs.execute("SELECT ap_id FROM airports WHERE iata='XXX'")
				qresult = curs.fetchall()
			except Error as e:
				db.close()
				return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

			if len(qresult) == 0:
				try:
					curs.execute("INSERT INTO airports (iata) VALUES ('XXX')")
					curs.execute("SELECT ap_id FROM airports WHERE iata='XXX'")
					qresult = curs.fetchall()
					ap_id = qresult[0][0]
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to get airport ID", version = vers)
			else:
				ap_id = qresult[0][0]

			# insert PREV EXP apart from ME/SE time
			try:
				curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic,
						pic_time, fo_time, dual, instructor, examiner, night, ifr, vfr) VALUES (
						"1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?,
						?, ?, ?, ?, ?, ?, ?, ?)
						''', (ap_id, ap_id, plane_id, tot_time, pic_id, pic_time, fo_time, dual, instr, exam, night, ifr, vfr,))
			except Error:
				db.close()
				return render_template("settings.html", col="red", msg="Error: Unable to add PREVEXP", version = vers)

			if mejet:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='MEJET'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('MEJET', 'MEJet')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='MEJET'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get MEJet ID", version = vers)
				else:
					plane_id = qresult[0][0]

				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic) 
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, mejet, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert MEJet", version = vers)
	
			if meprop:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='MEPROP'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('MEPROP', 'MEProp')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='MEPROP'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get MEProp ID", version = vers)
				else:
					plane_id = qresult[0][0]

				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic)
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, meprop, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert MEProp", version = vers)

			if mepist:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='MEPIST'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('MEPIST', 'MEPist')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='MEPIST'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get MEPist ID", version = vers)

				else:
					plane_id = qresult[0][0]

				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic)
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, mepist, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert MEProp", version = vers)

			if sejet:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='SEJET'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('SEJET', 'SEJet')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='SEJET'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get SEJet ID", version = vers)
				else:
					plane_id = qresult[0][0]
			
				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic)
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, sejet, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert SEJet", version = vers)

			if seprop:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='SEPROP'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('SEPROP', 'SEProp')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='SEPROP'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get SEProp ID", version = vers)
				else:
					plane_id = qresult[0][0]

				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic)
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, seprop, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert SEProp", version = vers)

			if sepist:
				# Check PREV EXP plane X
				try:
					curs.execute("SELECT plane_id FROM planes WHERE tail='SEPIST'")
					qresult = curs.fetchall()
				except Error as e:
					db.close()
					return render_template("settings.html", col="red", msg="Error: " + str(e), version = vers)

				if len(qresult) == 0:
					try:
						curs.execute("INSERT INTO planes (tail, class) VALUES ('SEPIST', 'SEPist')")
						curs.execute("SELECT plane_id FROM planes WHERE tail='SEPIST'")
						qresult = curs.fetchall()
						plane_id = qresult[0][0]
					except Error:
						db.close()
						return render_template("settings.html", col="red", msg="Error: Unable to get SEPist ID", version = vers)
				else:
					plane_id = qresult[0][0]

				try:
					curs.execute('''INSERT INTO flights (date, flt_nr, dep, dep_time, arr, arr_time, reg, tot_time, pic)
							VALUES ("1970-01-01", "PREVEXP", ?, "1970-01-01 00:00:00", ?, "1970-01-01 00:00:00", ?, ?, ?)
							''', (ap_id, ap_id, plane_id, sepist, pic_id,))
				except Error:
					db.close()
					return render_template("settings.html", col="red", msg="Error: Unable to insert SEPist", version = vers)

			db.commit()

			# get settings from DB
			try:
				curs.execute("SELECT name, role from settings")
				qresult = curs.fetchall()
				db.close()
			except Error:
				db.close()
				return render_template("settings.html", col="red", msg="Unable to access settings", version = vers)

			if len(qresult) != 0:
				return render_template("settings.html", col="green", msg="Previous experience added successfully", name = qresult[0][0], role = qresult[0][1], version = vers)
			else:
				return render_template("settings.html", col="green", msg="Previous experience added successfully", version = vers)

		else:
			return render_template("settings.html", col="red", msg="Error has occured: Invalid submition", version = vers)
	# If method GET
	else:
		db_name = str(session["user_id"]) + ".db"
		qresult = db_query(db_name, "SELECT name, role from settings")

		if type(qresult) != list:
			return render_template("settings.html", col="red", msg="Unable to access settings", version = vers)

		if len(qresult) != 0:
			return render_template("settings.html", name = qresult[0][0], role = qresult[0][1], version = vers)
		else:
			return render_template("settings.html", version = vers)

#-------------------------------------------------------- ERRORS
def errorhandler(e):
	if not isinstance(e, HTTPException):
		e = InternalServerError()
	return render_template("error.html", ename=e.name, ecode=e.code)


# Listen for errors
for code in default_exceptions:
	app.errorhandler(code)(errorhandler)


