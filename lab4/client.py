from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

import config

import json
import base64
import urllib
import hashlib
import httplib
from datetime import datetime, timedelta
import random
import sys

app = Flask(__name__)
app.secret_key = config.CLIENT_SECRET

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Charset": "utf-8"}

def get_server_response(url, html, data):
	data = urllib.urlencode(data)

	server_connection = httplib.HTTPConnection(config.CLIENT_HOST, config.SERVER_PORT)
	server_connection.request("GET", url, data, headers)
	response = server_connection.getresponse()
	response_text = response.read()
	file = open(html, "w")
	file.write(response_text)
	file.close()

def post_server_response(url, data):
	data = urllib.urlencode(data)

	server_connection = httplib.HTTPConnection(config.CLIENT_HOST, config.SERVER_PORT)
	server_connection.request("POST", url, data, headers)
	response = server_connection.getresponse()
	response_headers = response.getheaders()
	response_text = response.read()
	return response_text

@app.route("/", methods=["GET"])
def welcome():
	if request.method == "GET":
		if request.cookies.get("username") and request.cookies.get("user_cookie") and request.cookies.get("time_stamp"):
			return redirect("/home")
		return render_template("/html/index.html")

@app.route("/home", methods=["GET"])
def homepage():
	if request.method == "GET":
		username = request.cookies.get("username")
		user_cookie = request.cookies.get("user_cookie")
		time_stamp = request.cookies.get("time_stamp")
		if not (username and user_cookie and time_stamp):
			return redirect("/")

		data = {"username": username, 
				"user_cookie": user_cookie, 
				"time_stamp": time_stamp}
		response_text = post_server_response("/home", data)
		response_text = json.loads(response_text)
		if response_text['success']:
			return render_template("/html/homepage.html")
		response = make_response(redirect("/"))
		response.set_cookie("username", expires=0)
		response.set_cookie("user_cookie", expires=0)
		response.set_cookie("time_stamp", expires=0)
		return response		

@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":
		username = request.form["username"]
		hashed_password = request.form["password"]
		public_key = request.files["public_key"]
		public_key = public_key.stream.read()

		data = {"username": username, "password": hashed_password, "public_key": public_key}
		response_text = post_server_response("/register", data)
		response_text = json.loads(response_text)
		if (response_text['success']):
			expire_date = response_text["expire_date"]
			expire_date = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S.%f")
			response = make_response(json.dumps({'success' : True}), status.HTTP_200_OK)
			response.set_cookie("username", value=username, expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("user_cookie", value=response_text["cookie"], expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("time_stamp", value=response_text["time_stamp"], expires=expire_date, max_age=config.MAX_LIFE)
			return response
		else:
			response = make_response(json.dumps({'success' : False, 'error' : response_text['error']}), status.HTTP_200_OK)
			return response

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		username = request.form["username"]
		hashed_password = request.form["password"]
		private_key = request.files["private_key"]
		private_key = private_key.stream.read().decode('utf-8').strip()
		private_key = private_key.encode('ascii', 'ignore')
		private_key = RSA.importKey(private_key)

		hashed_password = hashed_password.encode("utf-8")

		random.seed(random.randint(1, sys.maxint))
		nonce = random.randint(1, sys.maxint)
		hashed_password_with_nonce = hashlib.sha512(hashed_password + str(nonce)).hexdigest()
		login_message = json.dumps({'encrypted_hashed_password': hashed_password_with_nonce, 'nonce': nonce})

		encrypted_login_message = private_key.decrypt(login_message)
		encrypted_login_message = base64.b64encode(encrypted_login_message)

		data = {"username": username, "password": encrypted_login_message}
		response_text = post_server_response("/login", data)
		response_text = json.loads(response_text)
		if (response_text['success']):
			expire_date = response_text["expire_date"]
			expire_date = datetime.strptime(expire_date, "%Y-%m-%d %H:%M:%S.%f")
			expire_date = response_text["expire_date"]
			response = make_response(json.dumps({'success' : True}), status.HTTP_200_OK)
			response.set_cookie("username", value=username, expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("user_cookie", value=response_text["cookie"], expires=expire_date, max_age=config.MAX_LIFE)
			response.set_cookie("time_stamp", value=response_text["time_stamp"], expires=expire_date, max_age=config.MAX_LIFE)
			return response
		else:
			response = make_response(json.dumps(response_text), status.HTTP_200_OK)
			return response

@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		username = request.cookies.get("username")
		user_cookie = request.cookies.get("user_cookie")
		time_stamp = request.cookies.get("time_stamp")
		data = {"username": username, "user_cookie": user_cookie, "time_stamp": time_stamp}
		response_text = post_server_response("/logout", data)
		response_text = json.loads(response_text)
		if (response_text['success']):
			response = make_response(redirect("/"))
			response.set_cookie("username", expires=0)
			response.set_cookie("user_cookie", expires=0)
			response.set_cookie("time_stamp", expires=0)
			return response

if __name__ == "__main__":
	app.run(config.SERVER_HOST, config.CLIENT_PORT, ssl_context=('server.crt', 'server.key'))
	# app.run(config.SERVER_HOST, config.CLIENT_PORT)
