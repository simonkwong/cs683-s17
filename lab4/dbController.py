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
								  port=config.DB_INFO['port'],
								  charset='utf8')

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
					hash VARCHAR(1024) DEFAULT NULL,
					cookie VARCHAR(1024) DEFAULT NULL,
					public_key VARCHAR(2048) DEFAULT NULL
					) ENGINE=InnoDB DEFAULT CHARSET=utf8
				"""

		self.execute_query(query)
		return True

	def is_username_available(self, username):
		query = """ SELECT username FROM users WHERE username = '%s'
				""" % username
		return self.fetch_one(query)

	def add_user(self, username, hashed_password, cookie, public_key):
		if not self.is_username_available(username):
			query = """ INSERT INTO users (username, hash, cookie, public_key) 
						VALUES ("%s", "%s", "%s", "%s")
					""" % (username, hashed_password, cookie, public_key)
			self.execute_query(query)
			return True
		return False

	def kill_user(self, username):
		query = """ DELETE FROM users WHERE username = "%s" """ % username
		self.execute_query(query)
		return True

	def verify_user(self, username, hashed_password):
		if self.is_username_available(username):
			query = """ SELECT * FROM users WHERE username = "%s"
					""" % username
			user = self.fetch_one(query)
			user = str(user["hash"])
			return (user == hashed_password)
		return False

	def get_user_public_key(self, username):
		query = """ SELECT public_key FROM users WHERE username = "%s"
				""" % username
		public_key = self.fetch_one(query)
		return public_key.get('public_key')

	def update_cookie(self, username, cookie):
		if self.is_username_available(username):
			query = """ UPDATE users SET cookie = "%s" WHERE username = "%s"
					""" % (cookie, username)
			self.execute_query(query)
			return True
		return False

	def get_cookie(self, username):
		if self.is_username_available(username):
			query = """ SELECT cookie FROM users WHERE username = "%s"
					""" % username
			return self.fetch_one(query)
		return None