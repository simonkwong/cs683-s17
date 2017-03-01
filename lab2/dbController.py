import MySQLdb
import hashlib
import crypt
import os
import binascii

import config


class DbController():
	def __init__(self):
		self.db = MySQLdb.connect(host=config.DB_INFO['host'],
								  user=config.DB_INFO['user'],
								  passwd=config.DB_INFO['password'],
								  db=config.DB_INFO['database'],
								  port=config.DB_INFO['port'])

	def execute_query(self, query):
		try:
			self.cur = self.db.cursor()
			self.cur.execute(query)
			newId = self.cur.lastrowid
			self.db.commit()
		except MySQLdb.Error, exc:
			raise exc
		finally:
			self.cur.close()
		return newId

	def fetch_one(self, query):
		self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		self.cur.execute(query)
		return self.cur.fetchone()

	def fetch_all(self, query):
		self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		self.cur.execute(query)
		return self.cur.fetchall()

	def create_user_table(self):
		query = """ CREATE TABLE IF NOT EXISTS users (
					user_id INT(16) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
					username VARCHAR(128) NOT NULL,
					salt VARCHAR(128) DEFAULT NULL,
					hash VARCHAR(512) DEFAULT NULL,
					cookie VARCHAR(512) DEFAULT NULL,
					public_key VARCHAR(2048) DEFAULT NULL
					)
				"""

		self.execute_query(query)
		return True

	def is_username_available(self, username):
		query = """ SELECT username FROM users WHERE username = '%s'
				""" % username
		return self.fetch_one(query)

	def add_user(self, username, hashed_password, cookie, public_key):
		if not self.is_username_available(username):
			# salt = salt = binascii.b2a_hex(os.urandom(64))
			# hashed = hashlib.sha512(password + salt).hexdigest()

			query = """ INSERT INTO users (username, hash, cookie, public_key) 
						VALUES ("%s", "%s", "%s", "%s")
					""" % (username, hashed_password, cookie, public_key)
			user_id = self.execute_query(query)
			return True
		return False

	def verify_user(self, username, hashed_password):
		if self.is_username_available(username):
			query = """ SELECT * FROM users WHERE username = "%s"
					""" % username
			user = self.fetch_one(query)
			return (user["hash"] == hashed_password)
		return False
