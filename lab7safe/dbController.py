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

	def execute_query(self, query, args):
		try:
			self.cur = self.db.cursor()
			self.cur.execute(query, args)
			newId = self.cur.lastrowid
			self.db.commit()
		except MySQLdb.Error, exc:
			raise exc
		finally:
			self.cur.close()
		return newId

	def fetch_one(self, query, args):
		self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		self.cur.execute(query, args)
		return self.cur.fetchone()

	def fetch_all(self, query, args):
		self.cur = self.db.cursor(MySQLdb.cursors.DictCursor)
		self.cur.execute(query, args)
		return self.cur.fetchall()

	def create_user_table(self):
		query = """ CREATE TABLE IF NOT EXISTS users (
					user_id INT(16) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
					username VARCHAR(128) NOT NULL,
					salt VARCHAR(128) DEFAULT NULL,
					hash VARCHAR(1024) DEFAULT NULL,
					cookie VARCHAR(1024) DEFAULT NULL,
					time_stamp VARCHAR(128) DEFAULT NULL,
					public_key VARCHAR(2048) DEFAULT NULL,
					nonce INT(16) UNSIGNED DEFAULT NULL
					) ENGINE=InnoDB DEFAULT CHARSET=utf8
				"""

		self.execute_query(query, [])
		return True

	def create_nonce_table(self):
		query = """ CREATE TABLE IF NOT EXISTS nonces (
					nonce_id INT(16) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
					nonce BIGINT(32) UNSIGNED NOT NULL
					) ENGINE=InnoDB DEFAULT CHARSET=utf8
				"""
		self.execute_query(query, [])
		return True

	def is_username_available(self, username):
		query = """ SELECT username FROM users WHERE username = %s"""
		return self.fetch_one(query, [username])

	def add_user(self, username, hashed_password, cookie, time_stamp):
		if not self.is_username_available(username):
			query = """ INSERT INTO users (username, hash, cookie, time_stamp) 
						VALUES (%s, %s, %s, %s)
					""" 
			self.execute_query(query, [username, hashed_password, cookie, time_stamp])
			return True
		return False

	def kill_user(self, username):
		query = """ DELETE FROM users WHERE username = %s """
		self.execute_query(query, [username])
		return True

	def verify_user(self, username, encrypted_hashed_password_with_nonce, nonce):
		if self.is_username_available(username):
			query = """ SELECT * FROM users WHERE username = %s
					"""
			user = self.fetch_one(query, [username])
			stored_hashed_password = str(user["hash"])

			validating_hashed_password_with_nonce = hashlib.sha512(stored_hashed_password + str(nonce)).hexdigest()

			return (validating_hashed_password_with_nonce == encrypted_hashed_password_with_nonce)
		return False

	def verify_user(self, username, hashed_password):
		if self.is_username_available(username):
			query = """ SELECT hash FROM users WHERE username = %s
					"""
			stored_hash = self.fetch_one(query, [username])
			stored_hash = str(stored_hash["hash"])

			return stored_hash == hashed_password
		return False

	def update_cookie(self, username, cookie, time_stamp):
		if self.is_username_available(username):
			query = """ UPDATE users SET cookie = %s, time_stamp = %s WHERE username = %s
					"""
			self.execute_query(query, [cookie, time_stamp, username])
			return True
		return False

	def get_cookie(self, username):
		if self.is_username_available(username):
			query = """ SELECT cookie, time_stamp FROM users WHERE username = %s
					"""
			return self.fetch_one(query, [username])
		return None

	def add_nonce(self, nonce):
		query = """ INSERT INTO nonces (nonce) VALUES (%d) """
		nonce_id = self.execute_query(query, [nonce])
		return nonce_id

	def map_nonce(self, username, nonce_id):
		query = """ UPDATE users SET nonce = %d WHERE username = %s 
				""" 
		self.execute_query(query, [nonce_id, username])
		return True

	def verify_nonce(self, nonce):
		nonce = int(nonce)
		query = """ SELECT * FROM nonces WHERE nonce = %d """ % int(nonce)
		nonce = self.fetch_one(query, [nonce])
		if nonce is None:
			return True
		return False