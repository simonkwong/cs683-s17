from flask import Flask, render_template, url_for, request

from dbController import DbController
import config

import json


app = Flask(__name__)

@app.route("/")
def welcome():
	db = DbController()
	db.create_user_table()
	return render_template("/html/index.html")

@app.route("/home")
def homepage():
	return render_template("/html/homepage.html")

@app.route("/login", methods=["POST"])
def login():
	if request.method == "POST":
		pass

@app.route("/register", methods=["POST"])
def register():
	if request.method == "POST":
		username = request.form("username")
		password = request.form("password")
		return json.dumps({'success' : True}), 200, {'ContentType' : 'application/json'} 

if __name__ == "__main__":
	app.run(config.HOST, config.PORT)