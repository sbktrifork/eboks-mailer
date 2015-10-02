#!/usr/bin/env python

# -*- coding: utf-8 -*-


import mimetypes 
import re
import smtplib
import sys
import unicodedata

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders

import requests
import yaml
from bs4 import BeautifulSoup

def slugify(text):
    text = unicodedata.normalize('NFKD', text).lower()
    return re.sub(r'\W+', '_', text)

config = yaml.load(file(sys.argv[1], "r").read())

LOGIN_URL = "https://m.e-boks.dk/logon.aspx"
INBOX_URL = "https://m.e-boks.dk/inbox.aspx"
DOC_URL = "https://m.e-boks.dk/inbox_document.aspx"
DOCVIEW_URL = "https://m.e-boks.dk/%s"

HEADERS = {'User-agent': 'Mozilla/5.0 (Linux; U;) Mobile'}

s = requests.Session()
s.headers.update(HEADERS)

print "[*] Fetching tokens from login page"

r = s.get(LOGIN_URL)
r.raise_for_status()

soup = BeautifulSoup(r.content)
viewstate = soup.select("#__VIEWSTATE")[0]['value']
eventvalidation = soup.select("#__EVENTVALIDATION")[0]['value']

form = {
    "__EVENTTARGET": "lnkOk",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": viewstate,
    "__VIEWSTATEENCRYPTED": "",
    "__EVENTVALIDATION": eventvalidation,
    "Identity": config["cpr"],
    "Password": config["password"],
    "ActivationCode": config["activation"]
}

print "[*] Sending login request"

r = s.post(LOGIN_URL, data=form)
r.raise_for_status()

if "notification warning" in r.content:
    print "[-] Login FAILED"
    exit(1)

print "[+] Login OK"


r = s.get(INBOX_URL)
r.raise_for_status()

soup = BeautifulSoup(r.content)
msgs = soup.select("#messages_form")[0]

auth = msgs.select("input[name=auth]")[0]["value"]
fuid = msgs.select("input[name=fuid]")[0]["value"]

for msg in msgs.select("li"):
    
    unread = len(msg.select(".item_unread")) == 1

    if unread:

        msgid = msg.a["href"].split("'")[1]
        date = msg.select("span.recieved")[0].text
        sender = msg.select("span.sender")[0].text
        subject = msg.select("span.title")[0].text

        print "[*] Getting documents:", date, repr(sender), repr(subject)

        form = {"target": msgid, "auth": auth, "fuid": fuid}
        r = s.post(DOC_URL, data=form)
        r.raise_for_status()

        soup = BeautifulSoup(r.content)

        msg = MIMEMultipart()
        msg['Subject'] = subject 
        msg['From'] = config["from"] % sender
        msg['To'] = config["to"]
      
        for el in soup.select("form li a"):

            url = el["href"]
            title = el["title"]
            filetype = el.select("span.info")[0].text[1:].split(",", 1)[0].lower()
            filename = slugify(unicode(title)) + "." + filetype
            mime = mimetypes.guess_type(filename)[0]

            print "[*] Downloading attachment:", filename

            r = s.get(DOCVIEW_URL % url)
            r.raise_for_status()
            
            part = MIMEBase(*mime.split("/"))
            part.set_payload(r.content)
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % filename)
            msg.attach(part)

        server = smtplib.SMTP(config["server"])
        server.sendmail(config["from"] % sender, config["to"], msg.as_string())
        