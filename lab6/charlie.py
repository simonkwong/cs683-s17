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
app.secret_key = config.CHARLIE_SECRET

charlie_private_key = ""
charlie_public_key = ""
bob_public_key = ""
alice_public_key = ""

session_key_with_alice = ""
session_key_with_bob = ""
nonce = ""

@app.route("/initiatehandshake", methods=["POST"])
def initiatehandshake():
	if request.method == "POST":
		global nonce, session_key_with_alice, session_key_with_bob

		response_text = config.get_response("GET", "/getpublickey", {}, config.BOB_PORT)
		response_text = json.loads(response_text)
		bob_public_key = response_text["public_key"]

		c_priv_key = RSA.importKey(charlie_private_key)
		c_pub_key = RSA.importKey(charlie_public_key)
		b_pub_key = RSA.importKey(bob_public_key)
		a_pub_key = RSA.importKey(alice_public_key)

		message = request.form["message"]
		message = base64.b64decode(message)
		message = c_priv_key.decrypt(message)
		message = json.loads(message)

		user_name = message['message']
		session_key_with_alice = message['session_key']

		session_key_with_bob = config.generate_key()

		data = json.dumps({"message": str(user_name), "session_key": session_key_with_bob})
		data = b_pub_key.encrypt(data, None)
		data = data[0]
		data = base64.b64encode(data)
		data = {"message": data}

		response_text = config.get_response("POST", "/initiatehandshake", data, config.BOB_PORT)
		response_text = json.loads(response_text)
		if response_text['success']:
			message = response_text['message']
			message = config.aes_decrypt(message, session_key_with_bob)
			message = json.loads(message)
			nonce = message['nonce']
			message = message['message']

			data = json.dumps({'message': message, 'nonce': nonce})
			encrypted_message = config.aes_encrypt(data, session_key_with_alice)

			response = make_response(json.dumps({'success': True, 'message': encrypted_message}), status.HTTP_200_OK)
			return response

		response = make_response(json.dumps({'success': False, 'error': 'Handshake Failed'}), status.HTTP_200_OK)
		return response

@app.route("/verifyhandshake", methods=["POST"])
def verifyhandshake():
	if request.method == "POST":
		global nonce, session_key_with_alice, session_key_with_bob

		message = request.form['message']
		signature = request.form['signature']
		signature = (long(signature),)

		nonce = int(nonce)

		a_pub_key = RSA.importKey(alice_public_key)

		verified = a_pub_key.verify(int(nonce), signature)

		if verified:
			signature = signature[0]
			data = json.dumps({'message': message, 'signature': signature})
			data = config.aes_encrypt(data, session_key_with_bob)
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
	return make_response(json.dumps({"public_key": charlie_public_key}))

if __name__ == "__main__":
	private_key = RSA.generate(config.KEY_SIZE)
	charlie_private_key = private_key.exportKey('PEM')
	charlie_public_key = private_key.publickey().exportKey('PEM')
	response_text = config.get_response("GET", "/getpublickey", {}, config.ALICE_PORT)
	response_text = json.loads(response_text)
	alice_public_key = response_text["public_key"]
	app.run(config.HOST, config.CHARLIE_PORT)
