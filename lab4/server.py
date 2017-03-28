from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

from dbController import DbController
import config

import json
import base64
import urllib
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = config.SERVER_SECRET

def validate_cookie(username, user_cookie, time_stamp):
	db = DbController()
	stored_user_cookie = db.get_cookie(username)
	if stored_user_cookie is not None:
		stored_time_stamp = stored_user_cookie['time_stamp']
		stored_user_cookie = stored_user_cookie['cookie']
	else:
		return False

	cur_timestamp = datetime.now()
	time_stamp = datetime.strptime(time_stamp, "%Y-%m-%d %H:%M:%S.%f")
	expire_date = time_stamp + timedelta(days=0, seconds=config.MAX_LIFE)

	if expire_date < cur_timestamp:
		return False

	validating_cookie = hashlib.sha512(app.secret_key + username + str(time_stamp)).hexdigest()

	if (str(stored_user_cookie) == str(user_cookie)) and (str(stored_user_cookie) == validating_cookie):
		return True
	return False

@app.route("/", methods=["GET"])
def welcome():
	if request.method == "GET":
		if request.cookies.get("username") and request.cookies.get("user_cookie") and request.cookies.get("time_stamp"):
			return redirect("/home")
		return render_template("/html/index.html")

@app.route("/home", methods=["POST"])
def homepage():
	if request.method == "POST":
		username = request.form["username"]
		user_cookie = request.form["user_cookie"]
		time_stamp = request.form["time_stamp"]
		if not (username and user_cookie and time_stamp):
			return make_response(json.dumps({'success': False}), status.HTTP_200_OK)
		if validate_cookie(username, user_cookie, time_stamp):
			return make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		return make_response(json.dumps({'success': False}), status.HTTP_200_OK)		

@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":
		expire_date = datetime.now()
		expire_date = expire_date + timedelta(days=0, seconds=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		public_key = request.form["public_key"]

		cur_timestamp = datetime.now()
		cur_timestamp = str(cur_timestamp)
		cookie = hashlib.sha512(app.secret_key + username + cur_timestamp).hexdigest()

		db = DbController()
		if db.add_user(username, hashed_password, cookie, cur_timestamp, public_key):
			response = make_response(json.dumps({'success' : True, 'cookie' : cookie, 'time_stamp': cur_timestamp, 'expire_date': str(expire_date)}), status.HTTP_200_OK)
			response.set_cookie("username", value=username, expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("user_cookie", value=cookie, expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("time_stamp", value=cur_timestamp, expires=expire_date, max_age=config.MAX_LIFE)
			return response
		else :
			response = make_response(json.dumps({'success' : False, 'error' : 'Username Is Already In Use.'}), status.HTTP_200_OK)
			return response

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		db = DbController()
		expire_date = datetime.now()
		expire_date = expire_date + timedelta(days=0, seconds=config.MAX_LIFE)
		username = request.form["username"]
		encrypted_login_message = request.form["password"]

		encrypted_login_message = base64.b64decode(encrypted_login_message)

		if not db.is_username_available(username):
			response = make_response(json.dumps({'success' : False, 'error' : 'Unknown User'}), status.HTTP_200_OK)
			return response
		else:
			public_key = db.get_user_public_key(username)
			public_key = public_key.encode('ascii', 'ignore')
			public_key = RSA.importKey(public_key)
			encrypted_login_message = public_key.encrypt(encrypted_login_message, None)
			encrypted_login_message = encrypted_login_message[0]
			encrypted_login_message = json.loads(encrypted_login_message)

			encrypted_hashed_password_with_nonce = encrypted_login_message["encrypted_hashed_password"]
			nonce = encrypted_login_message["nonce"]

			if db.verify_nonce(nonce):
				db.add_nonce(nonce)
			else:
				response = make_response(json.dumps({'success': False, 'error': 'Nonce Already Used. Try Again.'}), status.HTTP_200_OK)
				return response

			if db.verify_user(username, encrypted_hashed_password_with_nonce, nonce):
				cur_timestamp = datetime.now()
				cur_timestamp = str(cur_timestamp)
				cookie = hashlib.sha512(app.secret_key + username + cur_timestamp).hexdigest()
				db.update_cookie(username, cookie, cur_timestamp)
				response = make_response(json.dumps({'success' : True, "cookie": cookie, 'time_stamp': cur_timestamp, 'expire_date': str(expire_date)}), status.HTTP_200_OK)
				response.set_cookie("username", value=username, expires=expire_date, max_age=config.MAX_LIFE)
				response.set_cookie("user_cookie", value=cookie, expires=expire_date, max_age=config.MAX_LIFE)
				response.set_cookie("time_stamp", value=cur_timestamp, expires=expire_date, max_age=config.MAX_LIFE)
				return response
			else :
				response = make_response(json.dumps({'success' : False, 'error' : 'Incorrect Password'}), status.HTTP_200_OK)
				return response


@app.route("/logout", methods=["POST"])
def logout():
	if request.method == "POST":
		db = DbController()
		username = request.form["username"]
		user_cookie = request.form["user_cookie"]
		time_stamp = request.form["time_stamp"]
		db.update_cookie(username, "", time_stamp)
		response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		response.set_cookie("username", expires=0)
		response.set_cookie("user_cookie", expires=0)
		response.set_cookie("time_stamp", expires=0)
		return response

if __name__ == "__main__":
	db = DbController()
	db.create_user_table()
	db.create_nonce_table()
	app.run(config.SERVER_HOST, config.SERVER_PORT)
