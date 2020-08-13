import os, hashlib, binascii, urllib.parse

from flask import redirect, render_template, session
from functools import wraps

def login_required(f):
	"""
	Decorate routes to require login.

	http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if session.get("user_id") is None:
			return redirect("/login")
		return f(*args, **kwargs)
	return decorated_function

def escape(s):
    """
    Escape special characters.

    https://github.com/jacebrowning/memegen#special-characters
    """
    for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                     ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
        s = s.replace(old, new)
    return s

# from https://www.vitoshacademy.com/hashing-passwords-in-python/
def hash_password(password):
	"""Hash a password for storing."""
	salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
	pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
									salt, 100000)
	pwdhash = binascii.hexlify(pwdhash)
	return (salt + pwdhash).decode('ascii')

def verify_password(stored_password, provided_password):
	"""Verify a stored password against one provided by user"""
	salt = stored_password[:64]
	stored_password = stored_password[64:]
	pwdhash = hashlib.pbkdf2_hmac('sha512',
									provided_password.encode('utf-8'),
									salt.encode('ascii'),
									100000)
	pwdhash = binascii.hexlify(pwdhash).decode('ascii')
	return pwdhash == stored_password

def convert_to_minutes(x):
	if x:
		total = 0
		a = 3600
		lst = x.split(":")
		for i in range(len(lst)):
			if lst[i].isdigit():
				lst[i] = int(lst[i])
			else:
				lst[i] = 0
		for i in range(len(lst)):
			total += lst[i] * a
			a = a / 60
 
		return int(total / 60)
	else:
		return 0;

def convert_to_time(x):
	if x:
		hours = (x - x % 60) / 60
		minutes = x % 60
		if minutes < 10: 
			return str(hours)[:-2] + ':0' + str(minutes)
		else:
			return str(hours)[:-2] + ':' + str(minutes)
	else: return 0

