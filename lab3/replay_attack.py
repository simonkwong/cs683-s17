from flask import Flask, render_template, request, redirect, jsonify, make_response

import pyshark
import datetime

def replay_attack():
	print "Starting Replay Attack"
	pcap_parser('resources/replay_attack.cap')

def pcap_parser(file):
	print "Parsing PCAP File"
	try:
		pcap = pyshark.FileCapture(file)
		print pcap
	except:
		print "Could Not Parse Provided PCAP File"

def download_html():
	pass

if __name__ == "__main__":
	replay_attack()
