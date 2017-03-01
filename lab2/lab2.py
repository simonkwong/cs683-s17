from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from OpenSSL import SSL
from Crypto.PublicKey import RSA

from dbController import DbController
import config

import json
import hashlib
import datetime

app = Flask(__name__)
app.secret_key = config.SERVER_SECRET

@app.route("/", methods=["GET"])
def welcome():
	if request.method == "GET":
		db = DbController()
		db.create_user_table()
		print request.cookies
		if request.cookies.get("username"):
			return redirect("/home")
		return render_template("/html/index.html")

@app.route("/home", methods=["GET"])
def homepage():
	if request.method == "GET":
		if not request.cookies.get("username"):
			return redirect("/")
		return render_template("/html/homepage.html")

@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		public_key = request.files["public_key"]
		public_key_data = public_key.stream.read().decode('utf-8').strip()

		cur_timestamp = datetime.datetime.now()
		cookie = hashlib.sha512(app.secret_key + username + hashed_password + str(cur_timestamp)).hexdigest()

		db = DbController()
		if db.add_user(username, hashed_password, cookie, public_key_data):
			response = make_response(redirect("/home"))
			response.set_cookie("username", value=cookie, expires=expire_date)
			return response, json.dumps({'success' : True})
		else :
			response = make_response(redirect(""))
			return response, json.dumps({'success' : False, 'error' : 'Username Is Already In Use.'})

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		db = DbController()
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		hashed_password_1 = app.secret_key
		private_key = request.files["private_key"]
		private_key_data = private_key.stream.read()
		public_key_data = db.get_user_public_key(username)

		private_key = RSA.importKey(open('resources/private.pem', 'r').read())
		public_key = RSA.importKey(open('resources/public.pem', 'r').read())

		crypt = private_key.decrypt(hashed_password_1)
		decrypt = public_key.encrypt(crypt, None)

		if db.verify_user(username, hashed_password):
			cur_timestamp = datetime.datetime.now()
			cookie = hashlib.sha512(app.secret_key + username + hashed_password + str(cur_timestamp)).hexdigest()
			response = make_response(redirect("/home"))
			response.set_cookie("username", value=cookie, expires=expire_date)
			return response, json.dumps({'success' : True})
		else :
			response = make_response(redirect(""))
			if not db.is_username_available(username):
				return response, json.dumps({'success' : False, 'error' : 'Unknown User'})
			else:
				return response, json.dumps({'success' : False, 'error' : 'Incorrect Password'})

@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		response = make_response(redirect("/"))
		response.set_cookie("username", expires=0)
		return response

if __name__ == "__main__":
	# , ssl_context=('server.crt', 'server.key')
	app.run(config.HOST, config.PORT)
