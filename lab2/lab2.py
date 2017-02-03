from flask import Flask, render_template, url_for, request, redirect, jsonify, make_response

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
	app.run(config.HOST, config.PORT)



# 	Step 2. Cookies (by 2/3)
# Implement a login page that uses username/password. Do not use htaccess, and do not store the plaintext of the password on the server. Any passwords should be hashed before being stored. You don't have to use a database to store passwords. You may use salt, but it is not required. Set a permanent cookie once login is sucessful, i.e. the cookie does not expire. Implement a private page that requires this cookie, i.e. a page that only logged-in users can see. You may use PHP or javascript to set the cookie. (The university offers free training on Apache+PHP+MySQL at Lynda.com. Login to USF Connect, click on Learning Technologies, and then click on Lynda.com. You can search for Apache.)
# From the client web browser, visit your login page, and capture the packets to show how the username, password, and cookie is exchanged between the website to the browser. Close your web browser, visit the private page that requires cookie again, and capture the packets to show how the cookie is sent from your browser to the website. Clear the cookie in the web browser, and then visit the private page again, while capturing the packets. Your website should deny access to this page. Submit the source code of your login and private pages with the pcap file and README that explains how you implemented login and private pages.
# Read the article Logging out of facebook is not enough. https://www.nikcub.com/posts/logging-out-of-facebook-is-not-enough/ Create a Facebook account if you don't have one. Start packet capture. Login, logout, and visit 3rd-party websites (non-Facebook websites) with Like button such as this. http://www.dictionary.com/wordoftheday/ Submit the pcap file and show which packets send the Facebook cookies to Facebook when your browser visits the 3rd-party websites and README that explains what you can learn from these Facebook Cookies about your account.
# Add SSL to your website to support https for username/password login. Do not use htaccess, but implement a login page. Use Wireshark to verify that the passwords are not visible. You may use Apache-SSL. Submit the source code of your login page if it has changed and a README. The README should explain how you added SSL, and also whether the cookie is visible or not.