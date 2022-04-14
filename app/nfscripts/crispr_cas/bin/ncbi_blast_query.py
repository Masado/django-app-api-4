#!/usr/bin/env python3
import requests

import sys
import time
import re

query = sys.argv[1]

url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Put&QUERY="+query+"&DATABASE=nr&HITLIST_SIZE=10&PROGRAM=blastn&FILTER=L"
res = requests.get(url)

import re

m = re.search("RID = ([A-Z0-9]+)", res.text)

RID = m.group(1)
#print(res.content)

while True:
	getStatus = requests.get("https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID="+RID)
	requestStatus = re.search("Status=(.+?)QBlastInfoEnd", str(getStatus.content))
	status = requestStatus.groups("=")[0].split("\\")[0]

	if status == "WAITING":
		time.sleep(3)
	elif status == "READY":
		getStatus = requests.get("https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID="+RID)
	elif status == "UNKOWN":
		print("Unknown Status")
		break
	else:
		print("Blast Process Failed")		
		break

#Blast Ergebnisse in Datei speichern
with open("blast_query.fasta", "w") as f:
	f.write(getResult.text)