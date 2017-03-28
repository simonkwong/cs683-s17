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

@app.route("/", methods=["GET"])
def communicate():
	if request.method == "GET":
		response = make_response(json.dumps({'success': True}), status.HTTP_200_OK)
		return response

if __name__ == "__main__":
	app.run(config.HOST, config.BOB_PORT)
