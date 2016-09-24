#!/usr/bin/env python
# -*- coding: utf-8 -*-
# autoweek_nl.py
# version 0.1
# author: Bohdan Bobrowski bohdan@bobrowski.com.pl

import os
import glob
import json
import re
import sys
import pycurl
import urllib2
import hashlib
import requests
from slugify import slugify
from os import listdir
from os.path import isfile, join
from ConfigParser import ConfigParser

if(os.path.isfile('autoweek_nl.ini')):
    config = ConfigParser()
    config.read('autoweek_nl.ini')
else:
    config = ConfigParser()
    config.read('autoweek_nl.ini')
    config.add_section('account')
    config.set('account', 'login', '')
    config.set('account', 'password', '')
    config.add_section('brochuress')
    config.set('brochures', 'start', 1)
    config.set('brochures', 'stop', 4500)
    with open('autoweek_nl.ini', 'w') as configfile:
        config.write(configfile)
LOGIN = config.get('account', 'login')
PASSWORD = config.get('account', 'password')
START = config.getint('brochures', 'start')
STOP = config.getint('brochures', 'stop')
if LOGIN == '' or PASSWORD == '':
    print u"Please fill autoweek_nl.ini file with your username and password"
    exit()

class WWWDownloader:
    def __init__(self):
        self.contents = ''
    def body_callback(self, buf):
        self.contents = self.contents + buf

class Storage:
    def __init__(self):
        self.contents = ''
        self.line = 0

    def store(self, buf):
        self.line = self.line + 1
        self.contents = "%s%i: %s" % (self.contents, self.line, buf)

    def __str__(self):
        return self.contents

def DownloadWebPage(url):
    try:
        www = WWWDownloader()
        c = pycurl.Curl()        
        c.setopt(c.URL, url)
        c.setopt(c.WRITEFUNCTION, www.body_callback)
        c.setopt(c.HEADER, 1);
        c.setopt(c.FOLLOWLOCATION, 1)
        c.setopt(c.CONNECTTIMEOUT, 30)
        c.setopt(c.TIMEOUT, 30)
        c.setopt(c.COOKIEFILE, './autoweek_nl.cookies')
        c.setopt(c.COOKIEJAR, './autoweek_nl.cookies')
        c.perform()
    except Exception, err:
        print "- Connection error."
        print err
        exit()
        www_html = ''            
    else:
        www_html = www.contents
    return www_html

# 1. Logowanie:
www_html = DownloadWebPage('http://www.autoweek.nl/myautoweek/login.php?cache=no')
csrf_token = re.findall("<input type=\"hidden\" name=\"csrf_token\" value=\"([^\"]+)\" />",www_html)
if len(csrf_token) > 0:
    csrf_token = csrf_token[0]
    print "Login to autoweek.nl with token: "+csrf_token
    www = WWWDownloader()
    c = pycurl.Curl()        
    c.setopt(c.URL, 'http://www.autoweek.nl/myautoweek/login.php?cache=no')
    c.setopt(c.WRITEFUNCTION, www.body_callback)
    c.setopt(c.HEADER, 1);
    c.setopt(c.FOLLOWLOCATION, 1)
    c.setopt(c.CONNECTTIMEOUT, 30)
    c.setopt(c.TIMEOUT, 30)
    c.setopt(c.COOKIEFILE, './autoweek_nl.cookies')
    c.setopt(c.COOKIEJAR, './autoweek_nl.cookies')
    c.setopt(pycurl.HTTPPOST, [('email', LOGIN), ('password', PASSWORD), ('staylogged','1'), ('cache','no'), ('csrf_token',csrf_token)])
    c.perform()
print "I'm logged in :-)"
for x in range(START, STOP):
    if len(glob.glob("./brochure"+str(x)+"_*.pdf")) == 0:
        temp_filename = 'brochure'+str(x)+'.pdf';
        fp = open(temp_filename, "wb")
        curl = pycurl.Curl()
        retrieved_headers = Storage()
        curl.setopt(pycurl.URL, "http://www.autoweek.nl/brochurepdf.php?id="+str(x)+"&cache=no")
        curl.setopt(pycurl.WRITEDATA, fp)
        curl.setopt(pycurl.COOKIEFILE, './autoweek_nl.cookies')
        curl.setopt(pycurl.COOKIEJAR, './autoweek_nl.cookies')
        curl.setopt(pycurl.HEADERFUNCTION, retrieved_headers.store)
        curl.perform()
        curl.close()
        fp.close()
        real_filename = re.findall('filename=(brochure[^\.]+)',str(retrieved_headers))
        if len(real_filename) > 0:
            real_filename = slugify(unicode(real_filename[0].decode('iso-8859-1').encode('utf-8'), 'utf-8')) + '.pdf'
            print "File '"+real_filename+"' downloaded"
            os.rename(temp_filename, real_filename)
        else:
            print temp_filename+" deleted!"
            os.remove(temp_filename)            
