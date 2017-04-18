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
import random
import sys

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
		if request.cookies.get("cookie_data"):
			return redirect("/home")
		response = make_response(render_template("/html/index.html"))
		return response

@app.route("/home", methods=["GET"])
def homepage():
	if request.method == "GET":
		cookie_data = request.cookies.get("cookie_data")

		if cookie_data is not None:
			cookie_data = json.loads(cookie_data)
			username = cookie_data['username']
			user_cookie = cookie_data['user_cookie']
			time_stamp = cookie_data['time_stamp']			

			if not (username and user_cookie and time_stamp):
				return redirect("/logout")
		
			if validate_cookie(username, user_cookie, time_stamp):
				response = make_response(render_template("/html/homepage.html"))

				expire_date = datetime.now()
				expire_date = expire_date + timedelta(days=0, seconds=config.MAX_LIFE)
				cur_timestamp = datetime.now()
				cur_timestamp = str(cur_timestamp)
				cookie = hashlib.sha512(app.secret_key + username + cur_timestamp).hexdigest()
				db.update_cookie(username, cookie, cur_timestamp)
				cookie_data = {"username": username, "user_cookie": cookie, "time_stamp": cur_timestamp}
				response.set_cookie("cookie_data", value=json.dumps(cookie_data), expires=expire_date, max_age=config.MAX_LIFE)

				return response

		return redirect("/logout")

@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":

		print "REGISTRATION"

		expire_date = datetime.now()
		expire_date = expire_date + timedelta(days=0, seconds=config.MAX_LIFE)
		
		username = request.form["username"]
		hashed_password = request.form["password"]
		
		cur_timestamp = datetime.now()
		cur_timestamp = str(cur_timestamp)
		cookie = hashlib.sha512(app.secret_key + username + cur_timestamp).hexdigest()

		db = DbController()
		if db.add_user(username, hashed_password, cookie, cur_timestamp):
			response = make_response(json.dumps({'success' : True, 'cookie' : cookie, 'time_stamp': cur_timestamp, 'expire_date': str(expire_date)}), status.HTTP_200_OK)
			
			cookie_data = {"username": username, "user_cookie": cookie, "time_stamp": cur_timestamp}
			response.set_cookie("cookie_data", value=json.dumps(cookie_data), expires=expire_date, max_age=config.MAX_LIFE)
			return response
		else:
			response = make_response(json.dumps({'success' : False, 'error' : 'Username Is Already In Use.'}), status.HTTP_200_OK)
			return response

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		db = DbController()
		expire_date = datetime.now()
		expire_date = expire_date + timedelta(days=0, seconds=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]


		print username
		print hashed_password

		if db.verify_user(username, hashed_password):
			cur_timestamp = datetime.now()
			cur_timestamp = str(cur_timestamp)
			cookie = hashlib.sha512(app.secret_key + username + cur_timestamp).hexdigest()
			db.update_cookie(username, cookie, cur_timestamp)
			response = make_response(json.dumps({'success' : True, "cookie": cookie, 'time_stamp': cur_timestamp, 'expire_date': str(expire_date)}), status.HTTP_200_OK)
			
			cookie_data = {"username": username, "user_cookie": cookie, "time_stamp": cur_timestamp}
			response.set_cookie("cookie_data", value=json.dumps(cookie_data), expires=expire_date, max_age=config.MAX_LIFE)
			return response
		else :
			response = make_response(json.dumps({'success' : False, 'error' : 'Incorrect Password'}), status.HTTP_200_OK)
			return response


@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		db = DbController()
		response = make_response(redirect("/"))
		response.set_cookie("cookie_data", expires=0)
		return response

if __name__ == "__main__":
	db = DbController()
	db.create_user_table()
	db.create_nonce_table()
	app.run(config.SERVER_HOST, config.SERVER_PORT)
