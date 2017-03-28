from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto.PublicKey import RSA

import config
import json
import base64
import urllib
import hashlib
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = config.ALICE_SECRET

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Charset": "utf-8"}

@app.route("/", methods=["GET"])
def home():
	if request.method == "GET":
		return render_template("/html/index.html")

@app.route("/bob", methods=["POST"])
def chat_with_bob():
	if request.method == "POST":

		user_name = request.form["user_name"]

		public_key = request.files["public_key"]
		public_key = public_key.stream.read().decode('utf-8').strip()
		public_key = public_key.encode('ascii', 'ignore')

		private_key = request.files["private_key"]
		private_key = private_key.stream.read().decode('utf-8').strip()
		private_key = private_key.encode('ascii', 'ignore')

		public_key = RSA.importKey(public_key)
		private_key = RSA.importKey(private_key)



		fresh_session_key = RSA.generate(config.KEY_SIZE)


		data = {"message"}

		response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		return response

@app.route("/mitm", methods=["POST"])
def mitm():
	if request.method == "POST":
		pass


def post_server_response(url, data):
	data = urllib.urlencode(data)

	server_connection = httplib.HTTPConnection(config.CLIENT_HOST, config.SERVER_PORT)
	server_connection.request("POST", url, data, headers)
	response = server_connection.getresponse()
	response_headers = response.getheaders()
	response_text = response.read()
	return response_text

if __name__ == "__main__":
	app.run(config.HOST, config.ALICE_PORT)
