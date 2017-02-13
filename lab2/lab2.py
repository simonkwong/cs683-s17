from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response
from OpenSSL import SSL

from dbController import DbController
import config

import json
import datetime

app = Flask(__name__)
app.secret_key = "CS683 Computer Security and Privacy"

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

@app.route("/login", methods=["GET", "POST"])
def login():
	expire_date = datetime.datetime.now()
	expire_date = expire_date + datetime.timedelta(days=90)
	
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		db = DbController()
		if db.verify_user(username, password):
			response = make_response(redirect("/home"))
			response.set_cookie("username", value=username, expires=expire_date)
			return response
		else :
			return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
	expire_date = datetime.datetime.now()
	expire_date = expire_date + datetime.timedelta(days=90)
	
	if request.method == "POST":
		username = request.form["username"]
		password = request.form["password"]
		db = DbController()
		if db.add_user(username, password):
			response = make_response(redirect("/home"))
			response.set_cookie("username", value=username, expires=expire_date)
			return response
		else :
			return redirect("/")

@app.route("/logout", methods=["GET"])
def logout():
	if request.method == "GET":
		response = make_response(redirect("/"))
		response.set_cookie("username", expires=0)
		return response

if __name__ == "__main__":
	# , ssl_context=('server.crt', 'server.key')
	app.run(config.HOST, config.PORT)
