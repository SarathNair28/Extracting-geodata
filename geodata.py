import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

api_key = False
# If you have a Google Places API key, enter it here
# api_key = 'AIzaSy___IDByT70'

if api_key is False:
    serviceurl = "http://py4e-data.dr-chuck.net/geojson?"
else :
    serviceurl = "https://maps.googleapis.com/maps/api/place/textsearch/json?"

conn=sqlite3.connect('geodata.sqlite')
cur=conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Location(Address TEXT,Geodata TEXT)''')

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fh=open('where.data')
count=0
for line in fh:
	if(count>200):
		print('Retreived 200 Locations, restart if you want to extract more')
		break
	adress=line.strip()
	print('')
	cur.execute("SELECT Geodata from Location where Address=?",(memoryview(adress.encode()),))
	try:
		cur.fetchone()[0]
		print("Found in Database ",adress)
		continue
	except:
		pass
	par=dict()
	par["query"]=adress
	if api_key is not False: par["key"]=api_key
	url=serviceurl+urllib.parse.urlencode(par)
	print("Retrieving ",url)
	uh=urllib.request.urlopen(url,context=ctx)
	data=uh.read().decode()
	print("retreived ",len(data))
	count=count+1
	
	try:
		js=json.loads(data)
	except:
		print(data) #incase if unicode causes error we print 
		continue
	if 'status' not in js or (js["status"]!='OK' and js["status"]!='ZERO_RESULTS'):
		print("Faliure to retreive")
		print(data) 
		break
	cur.execute("INSERT INTO Location (Address,Geodata) VALUES (?,?)",(memoryview(adress.encode()),memoryview(data.encode())))
	conn.commit()
