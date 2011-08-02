#!/usr/bin/python

"""
Copyright (c) Adam Strauch
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
   
    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDER "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import xmlrpclib, sys, base64, StringIO, gzip, re

import struct, os
from stat import *

def hashFile(name): 
	try: 
		longlongformat = 'q'  # long long 
		bytesize = struct.calcsize(longlongformat) 

		f = open(name, "rb") 

		filesize = os.path.getsize(name) 
		hash = filesize 
                    
		if filesize < 65536 * 2: 
			return "SizeError" 
                 
		for x in range(65536/bytesize): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF #to remain as 64bit number  


		f.seek(max(0,filesize-65536),0) 
		for x in range(65536/bytesize): 
			buffer = f.read(bytesize) 
			(l_value,)= struct.unpack(longlongformat, buffer)  
			hash += l_value 
			hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
		f.close() 
		returnedhash =  "%016x" % hash 
		return returnedhash 
    
	except(IOError): 
		return "IOError"

class SubException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SubLib:
	APIURL = "http://api.opensubtitles.org/xml-rpc"
	token = None
	proxy = None

	lang = "en"
	login = ""
	passwd = ""

	def __init__(self, login="", passwd=""):
		self.login = login
		self.passwd = passwd
		
	def connect(self):
		if not self.lang:
			raise SubException('No language set')
		if not self.APIURL:
			raise SubException('No APIURL set')

		try:
			self.proxy = xmlrpclib.ServerProxy(self.APIURL)
			self.token = self.proxy.LogIn(self.login, self.passwd, "en", "OS Test User Agent")["token"]
		except xmlrpclib.ProtocolError:
			raise SubException("Service unavailable")

	def query(self, queries, lang):
		requests = []
		results = []
		
		for q in queries:
			requests.append({"sublanguageid": lang, "query": q})

		#print self.proxy.SearchSubtitles(self.token, requests)
		data = self.proxy.SearchSubtitles(self.token, requests)["data"]


		if data:
			for x in data:
				results.append({
					"lang": x["LanguageName"],
					"filename": x["SubFileName"],
					"subId": int(x["IDSubtitleFile"]),
					"downloads": int(x["SubDownloadsCnt"]),
					"format": x["SubFormat"],
				})

		results.sort(key=lambda x: x["downloads"])
		results.reverse()

		return results
	
	#queries - Filenames
	def queryHash(self, queries, lang):
		requests = []
		results = []
		
		for q in queries:
			hash = hashFile(q)
			size = os.stat(q)[ST_SIZE]
			
			#print "\tHash is %s (%d)" % (hash, size)
			requests.append({"sublanguageid": lang, "moviehash": hash, "moviebytesize": size})
		
		#print self.proxy.SearchSubtitles(self.token, requests)
		data = self.proxy.SearchSubtitles(self.token, requests)["data"]
		#print data

		
		if data:
			for x in data:
				results.append({
					"lang": x["LanguageName"],
					"filename": x["SubFileName"],
					"subId": int(x["IDSubtitleFile"]),
					"downloads": int(x["SubDownloadsCnt"]),
					"format": x["SubFormat"],
				})
	
		results.sort(key=lambda x: x["downloads"])
		results.reverse()

		return results
	

	def download(self, subId, filename):
		data = self.proxy.DownloadSubtitles(self.token, [subId])["data"]

		if data:
			for x in data:
				sub = x["data"]
				sub = base64.b64decode(sub)
				substream = StringIO.StringIO(sub)
				gzipper = gzip.GzipFile(fileobj=substream)
				sub = gzipper.read()

				f = open(filename, "w")
				f.write(sub)
				f.close()
			
			return True

		return False

def handler(results, subfilename=None):
	if results:
		print "I found this:"
	
		i = 1
		for x in results:
			print "\t%d." % i, x["filename"].ljust(66), " - %d/%s" % (x["downloads"], x["lang"])
			i += 1

		print
		if len(results) > 1:
			try:
				num_for_download = int(raw_input("What number do you want download: "))
			except ValueError:
				print "Don't be like old lady! Use number at the beginning of line."
				sys.exit(1)
		else:
			num_for_download = 1

		try:
			print "I'll download subtitles %d with is %d" % (num_for_download, results[num_for_download-1]["subId"])
		except IndexError:
			print "Don't be like old lady! Use number from right range."
			sys.exit(1)

		if subfilename:
			sl.download(results[num_for_download-1]["subId"], subfilename + "." + results[num_for_download-1]["format"])
		else:
			sl.download(results[num_for_download-1]["subId"], results[num_for_download-1]["filename"])
			subfilename = results[num_for_download-1]["filename"]

		print 

		print "You can find your subtitles in:"
		print " \t%s" % subfilename		

		print
		print "Enjoy your video, bye bye"

	else:
		print "I found nothing :-("
	
	print
	print "This tool is released under BSD licence and it can't exists without opensubtitles.org."
	
	#sl.query(["Eureka.S03E17.HDTV.XviD-NoTV", "Eureka.S04E04.The.Story.of.O2.HDTV.XviD-FQM"], "cze")

def main():
	import argparse

	parser = argparse.ArgumentParser(description='Subtitles downloader')

	parser.add_argument('-q', default=False, dest="query", help='Search subtitles (by fulltext)', action='store_true')
	#parser.add_argument('-u', default=False, dest="upload",help='Upload subtitles of files', action='store_true')
	parser.add_argument('-d', default=False, dest="download",help='Download subtitles for files (by hash)', action='store_true')

	parser.add_argument('queries', metavar='file/query', type=str, nargs='+',
			help='video files or query')


	args = parser.parse_args()
	#print args
	
	sl = SubLib()
	sl.connect()
	
	if args.download:
		for query in args.queries:
			results = []
			
			results += sl.queryHash([query], "cze")
			subfilename = ".".join(query.split(".")[:-1])

			print "Looking subtitles for:"
			print
			print "\t%s" % query

			print
			
			handler(results)
	elif args.query:
		query = " ".join(args.queries)
		
		print "Looking subtitles for:"
		print
		print "\t%s" % query

		print
		
		results = sl.query([query] ,"cze")
			
		handler(results)
	
	else:
		print "Use -q or -d switcher"

if __name__ == "__main__":
	main()
	
	

