from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto.PublicKey import RSA

import config
import json
import base64
import urllib
import hashlib
import string, random
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = config.ALICE_SECRET

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Charset": "utf-8"}

alice_private_key = ""
alice_public_key = ""
bob_public_key = ""
charlie_public_key = ""

session_key = ""

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

		session_key = config.generate_key()

		data = json.dumps({"message": str(user_name), "session_key": session_key})
		data = b_pub_key.encrypt(data, None)
		data = data[0]
		data = base64.b64encode(data)
		data = {"message": data}

		response_text = config.get_response("POST", "/initiatehandshake", data, config.BOB_PORT)
		response_text = json.loads(response_text)
		if response_text['success']:
			message = response_text['message']
			message = config.aes_decrypt(message, session_key)
			message = json.loads(message)
			nonce = message['nonce']
			message = message['message']

			if message != user_name:
				response = make_response(json.dumps({'success': False, 'error': "This Isn't Bob."}))
				return response
			else:
				signature = a_priv_key.sign(nonce, None)
				signature = signature[0]

				data = json.dumps({'message': message, 'signature': signature})
				data = config.aes_encrypt(data, session_key)
				data = {'message': data}

				response_text = config.get_response("POST", "/verifyhandshake", data, config.BOB_PORT)
				response_text = json.loads(response_text)
				if response_text['success']:
					response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
					return response

		response = make_response(json.dumps({'success': False, 'error': 'Handshake Failed'}), status.HTTP_200_OK)
		return response

@app.route("/getpublickey", methods=["GET"])
def get_public_key():
	return make_response(json.dumps({"public_key": alice_public_key}))

@app.route("/mitm", methods=["POST"])
def mitm():
	if request.method == "POST":
		
		user_name = request.form["user_name"]

		response_text = config.get_response("GET", "/getpublickey", {}, config.CHARLIE_PORT)
		response_text = json.loads(response_text)
		charlie_public_key = response_text["public_key"]

		a_priv_key = RSA.importKey(alice_private_key)
		a_pub_key = RSA.importKey(alice_public_key)
		c_pub_key = RSA.importKey(charlie_public_key)

		session_key = config.generate_key()

		data = json.dumps({"message": str(user_name), "session_key": session_key})
		data = c_pub_key.encrypt(data, None)
		data = data[0]
		data = base64.b64encode(data)
		data = {"message": data}

		response_text = config.get_response("POST", "/initiatehandshake", data, config.CHARLIE_PORT)
		response_text = json.loads(response_text)
		if response_text['success']:
			message = response_text['message']
			message = config.aes_decrypt(message, session_key)
			message = json.loads(message)
			nonce = message['nonce']
			message = message['message']

			if message != user_name:
				response = make_response(json.dumps({'success': False, 'error': "This Isn't Charlie."}))
				return response
			else:
				signature = a_priv_key.sign(nonce, None)
				signature = signature[0]

				data = {'message': message, 'signature': signature}

				response_text = config.get_response("POST", "/verifyhandshake", data, config.CHARLIE_PORT)
				response_text = json.loads(response_text)
				if response_text['success']:
					response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
					return response

		response = make_response(json.dumps({'success': False, 'error': 'Handshake Failed'}), status.HTTP_200_OK)
		return response

if __name__ == "__main__":
	private_key = RSA.generate(config.KEY_SIZE)
	alice_private_key = private_key.exportKey('PEM')
	alice_public_key = private_key.publickey().exportKey('PEM')
	app.run(config.HOST, config.ALICE_PORT)
