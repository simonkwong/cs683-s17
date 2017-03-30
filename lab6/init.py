from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA

import json, base64, urllib, hashlib, httplib, string, random, sys
from datetime import datetime, timedelta

HOST = '0.0.0.0'

KEY_SIZE = 2048
SHARED_KEY_SIZE = 1024
BLOCK_SIZE = 32

ALICE_PORT = 3000
BOB_PORT = 3001
CHARLIE_PORT = 3002

ALICE_SECRET = 'ycavirP dna ytiruceS retupmoC 386SC'
BOB_SECRET = 'CS683 Computer Security and Privacy'
CHARLIE_SECRET = 'ycavirP dna ytiruceS retupmoC 386SC CS683 Computer Security and Privacy'

headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain", "Charset": "utf-8"}

def get_response(request_type, url, data, port):
	data = urllib.urlencode(data)

	server_connection = httplib.HTTPConnection(HOST, port)
	server_connection.request(request_type, url, data, headers)
	response = server_connection.getresponse()
	response_text = response.read()
	return response_text

def aes_encrypt(plaintext, key):
	iv = Random.new().read(AES.block_size)
	cipher = AES.new(key, AES.MODE_CFB, iv)
	return base64.b64encode(iv + cipher.encrypt(plaintext))

def aes_decrypt(encrypted, key):
	encrypted = base64.b64decode(encrypted)
	iv = encrypted[:AES.block_size]
	cipher = AES.new(key, AES.MODE_CFB, iv)
	return cipher.decrypt(encrypted[AES.block_size:]).decode('utf-8')

def generate_key():
	return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in xrange(BLOCK_SIZE))

def generate_nonce():
	random.seed(random.randint(1, sys.maxint))
	nonce = random.randint(1, sys.maxint)
	return nonce