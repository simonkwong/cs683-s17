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
import datetime

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
		if request.cookies.get("username"):
			return redirect("/home")
		return render_template("/html/index.html")

@app.route("/home", methods=["GET"])
def homepage():
	if request.method == "GET":
		print request.cookies.get("username")
		if not request.cookies.get("username"):
			return redirect("/")
		data = {"username": request.cookies.get("username")}
		response_text = post_server_response("/home", data)
		return render_template("/html/homepage.html")


@app.route("/register", methods=["POST"])
def register():	
	if request.method == "POST":
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		public_key = request.files["public_key"]
		public_key = public_key.stream.read()

		data = {"username": username, "password": hashed_password, "public_key": public_key}
		response_text = post_server_response("/register", data)
		response_text = json.loads(response_text)
		if (response_text['success']):
			response = make_response(json.dumps({'success' : True}), status.HTTP_200_OK)
			response.set_cookie("username", value=username, expires=expire_date)
			response.set_cookie("user_cookie", value=response_text["cookie"], expires=expire_date)
			response.set_cookie("time_stamp", value=response_text["time_stamp"], expires=expire_date)
			return response
		else:
			response = make_response(json.dumps({'success' : False, 'error' : response_text['error']}), status.HTTP_200_OK)
			return response

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		expire_date = datetime.datetime.now()
		expire_date = expire_date + datetime.timedelta(days=config.MAX_LIFE)
		username = request.form["username"]
		hashed_password = request.form["password"]
		private_key = request.files["private_key"]
		private_key = private_key.stream.read().decode('utf-8').strip()
		private_key = private_key.encode('ascii', 'ignore')
		private_key = RSA.importKey(private_key)

		hashed_password = hashed_password.encode("utf-8") #str
		encrypted_hashed_password = private_key.decrypt(hashed_password)
		encrypted_hashed_password = base64.b64encode(encrypted_hashed_password)

		data = {"username": username, "password": encrypted_hashed_password}
		response_text = post_server_response("/login", data)
		response_text = json.loads(response_text)
		if (response_text['success']):
			response = make_response(json.dumps({'success' : True}), status.HTTP_200_OK)
			response.set_cookie("username", value=username, expires=expire_date)
			response.set_cookie("user_cookie", value=response_text["cookie"], expires=expire_date)
			response.set_cookie("time_stamp", value=response_text["time_stamp"], expires=expire_date)
			return response
		else:
			response = make_response(json.dumps(response_text), status.HTTP_200_OK)
			return response

@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		response = make_response(redirect("/"))
		response.set_cookie("username", expires=0)
		return response

if __name__ == "__main__":
	# , ssl_context=('server.crt', 'server.key')
	app.run(config.SERVER_HOST, config.CLIENT_PORT)
