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
app.secret_key = config.BOB_SECRET

bob_public_key = ""
bob_private_key = ""
alice_public_key = ""

@app.route("/communicate", methods=["POST"])
def communicate():
	if request.method == "POST":

		response_text = config.get_response("GET", "/getpublickey", {}, config.ALICE_PORT)
		response_text = json.loads(response_text)

		alice_public_key = response_text["public_key"]

		b_pub_key = RSA.importKey(bob_public_key)
		b_priv_key = RSA.importKey(bob_private_key)
		a_pub_key = RSA.importKey(alice_public_key)


		message = request.form["message"]


		print message
		message = base64.b64decode(message)
		message = a_pub_key.encrypt(message, None)
		print message



		response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		return response

@app.route("/getpublickey", methods=["GET"])
def get_public_key():
	return make_response(json.dumps({"public_key": bob_public_key}))

if __name__ == "__main__":
	private_key = RSA.generate(config.KEY_SIZE)
	bob_private_key = private_key.exportKey('PEM')
	bob_public_key = private_key.publickey().exportKey('PEM')
	app.run(config.HOST, config.BOB_PORT)
