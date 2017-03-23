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
import datetime

app = Flask(__name__)
app.secret_key = config.SERVER_SECRET

def validate_cookie():
	pass

@app.route("/", methods=["GET"])
def welcome():
	if request.method == "GET":
		if request.cookies.get("username"):
			return redirect("/home")
		return render_template("/html/index.html")

@app.route("/home", methods=["POST"])
def homepage():
	if request.method == "POST":
		print request.form["username"]
		if not request.form["username"]:
			return redirect("/")
		return render_template("/html/homepage.html")

@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		public_key = request.form["public_key"]

		cur_timestamp = datetime.datetime.now()
		cookie = hashlib.sha512(app.secret_key + username + hashed_password + str(cur_timestamp)).hexdigest()

		db = DbController()
		if db.add_user(username, hashed_password, cookie, public_key):
			response = make_response(json.dumps({'success' : True, 'cookie' : cookie}), status.HTTP_200_OK)
			response.set_cookie("username", value=cookie, expires=expire_date)
			return response
		else :
			response = make_response(json.dumps({'success' : False, 'error' : 'Username Is Already In Use.'}), status.HTTP_200_OK)
			return response

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		db = DbController()
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		encrypted_hashed_password = request.form["password"]

		encrypted_hashed_password = base64.b64decode(encrypted_hashed_password)

		if not db.is_username_available(username):
			response = make_response(json.dumps({'success' : False, 'error' : 'Unknown User'}), status.HTTP_200_OK)
			return response
		else:
			public_key = db.get_user_public_key(username)
			public_key = public_key.encode('ascii', 'ignore')
			public_key = RSA.importKey(public_key)
			hashed_password = public_key.encrypt(encrypted_hashed_password, None)
			hashed_password = hashed_password[0]

			if db.verify_user(username, hashed_password):
				cur_timestamp = datetime.datetime.now()
				cookie = hashlib.sha512(app.secret_key + username + hashed_password + str(cur_timestamp)).hexdigest()
				response = make_response(json.dumps({'success' : True, "cookie": cookie}), status.HTTP_200_OK)
				response.set_cookie("username", value=cookie, expires=expire_date)
				return response
			else :
				response = make_response(json.dumps({'success' : False, 'error' : 'Incorrect Password'}), status.HTTP_200_OK)
				return response


@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		response = make_response(redirect("/"))
		response.set_cookie("username", expires=0)
		return response

if __name__ == "__main__":
	# , ssl_context=('server.crt', 'server.key')
	app.run(config.HOST, config.SERVER_PORT)
