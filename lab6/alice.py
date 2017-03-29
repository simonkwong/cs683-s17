from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto import Random
from Crypto.Cipher import AES
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

alice_private_key = ""
alice_public_key = ""
bob_public_key = ""
charlie_public_key = ""

@app.route("/", methods=["GET"])
def home():
	if request.method == "GET":
		return render_template("/html/index.html")

@app.route("/bob", methods=["POST"])
def chat_with_bob():
	if request.method == "POST":

		user_name = request.form["user_name"]

		response_text = config.get_response("GET", "/getpublickey", {}, config.BOB_PORT)
		response_text = json.loads(response_text)

		bob_public_key = response_text["public_key"]

		a_priv_key = RSA.importKey(alice_private_key)
		a_pub_key = RSA.importKey(alice_public_key)
		b_pub_key = RSA.importKey(bob_public_key)


		fresh_session_key = RSA.generate(config.SHARED_KEY_SIZE)
		fresh_session_key = fresh_session_key.exportKey('PEM')

		# fresh_session_key = "THIS IS A TEST"

		# fresh_session_key = a_pub_key.encrypt(fresh_session_key, None)
		# fresh_session_key = base64.b64encode(fresh_session_key)

		data = json.dumps({"message": str(user_name), "session_key": fresh_session_key})
		data = a_priv_key.decrypt(data)
		# data = data[0]
		data = base64.b64encode(data)
		data = {"message": data}

		response_text = config.get_response("POST", "/communicate", data, config.BOB_PORT)
		response_text = json.loads(response_text)
		print response_text

		response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		return response

@app.route("/getpublickey", methods=["GET"])
def get_public_key():
	return make_response(json.dumps({"public_key": alice_public_key}))

@app.route("/mitm", methods=["POST"])
def mitm():
	if request.method == "POST":
		pass

if __name__ == "__main__":
	private_key = RSA.generate(config.KEY_SIZE)
	alice_private_key = private_key.exportKey('PEM')
	alice_public_key = private_key.publickey().exportKey('PEM')
	app.run(config.HOST, config.ALICE_PORT)
