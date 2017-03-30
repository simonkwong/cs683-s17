from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from flask_api import status
from OpenSSL import SSL
from Crypto.PublicKey import RSA

import config
import json
import base64
import urllib
import hashlib
import ast
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = config.BOB_SECRET

bob_private_key = ""
bob_public_key = ""
alice_public_key = ""

session_key = ""
nonce = ""

@app.route("/initiatehandshake", methods=["POST"])
def initiatehandshake():
	if request.method == "POST":
		global nonce

		b_priv_key = RSA.importKey(bob_private_key)
		b_pub_key = RSA.importKey(bob_public_key)
		a_pub_key = RSA.importKey(alice_public_key)

		message = request.form["message"]
		message = base64.b64decode(message)
		message = b_priv_key.decrypt(message)
		message = json.loads(message)

		user_name = message['message']
		session_key = message['session_key']
		nonce = config.generate_nonce()

		data = json.dumps({'message': user_name, 'nonce': nonce})
		encrypted_message = config.aes_encrypt(data, session_key)

		response = make_response(json.dumps({'success': True, 'message': encrypted_message}), status.HTTP_200_OK)
		return response

@app.route("/verifyhandshake", methods=["POST"])
def verifyhandshake():
	if request.method == "POST":
		global nonce

		message = request.form['message']
		signature = request.form['signature']
		signature = (long(signature),)

		nonce = int(nonce)

		a_pub_key = RSA.importKey(alice_public_key)

		verified = a_pub_key.verify(int(nonce), signature)

		response = make_response(json.dumps({'success': verified}), status.HTTP_200_OK)
		return response

@app.route("/getpublickey", methods=["GET"])
def get_public_key():
	return make_response(json.dumps({"public_key": bob_public_key}))

if __name__ == "__main__":
	private_key = RSA.generate(config.KEY_SIZE)
	bob_private_key = private_key.exportKey('PEM')
	bob_public_key = private_key.publickey().exportKey('PEM')
	response_text = config.get_response("GET", "/getpublickey", {}, config.ALICE_PORT)
	response_text = json.loads(response_text)
	alice_public_key = response_text["public_key"]
	app.run(config.HOST, config.BOB_PORT)

# cookie = {nonce}
# userid, Ru<H(pwd, nonce)>