#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# Glenn Meyer - gmeyer1
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib
import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPRequest(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
	if(port == None):
	   port = 80
	
	# try to create socket
	try:	
		connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	except socket.error, msg:
		print('Failed to create socket. ' +
		'Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1])

	# try to connect to socket
	try:
		connection.connect((host,port))
	except socket.error, msg:
		print('Failed to connect. ' +
		'Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1])
        return connection

    # extract code from response
    def get_code(self, data):
        response = data.split("\r\n\r\n", 1)
	line = response[0].split("\r\n", 1)[0]
	code = int(line.split(" ")[1])
        return code

    # extract header from response (doesn't appear to be needed)
    def get_headers(self,data):
        return data.split('\r\n\r\n')[0]

    # extract body from response
    def get_body(self, data):
        return data.split('\r\n\r\n')[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    # perform HTTP GET
    def GET(self, url, args=None):
    	# parse URL
	url = urlparse.urlparse(url)
	directory = url.path
        if(directory == ''):
            directory = '/'
	
	# construct header	
	header = 'GET ' + directory + ' HTTP/1.1\r\n'
        header += 'Host: ' + url.hostname + '\r\n'
        header += 'Accept: */*\r\n'
        header += 'Connection: close\r\n'
        header += '\r\n'
	
	# connect and send request	
	connection = self.connect(url.hostname, url.port)
	connection.send(header)
	response = self.recvall(connection)
	
	# extract code and body from response	
        code = int(self.get_code(response))
        body = self.get_body(response)

        return HTTPRequest(code, body)

    # perform HTTP POST
    def POST(self, url, args=None):
    	# parse URL
	url = urlparse.urlparse(url)
        directory = url.path
        if(directory == ''):
            directory = '/'
	
	# get body and set length	
	if(args == None):
            bodyLen = 0;
        else:
            body = urllib.urlencode(args)
            bodyLen = len(body)            
	
	# construct header
        header = 'POST ' + directory + ' HTTP/1.1\r\n'
        header += 'Host: ' + url.hostname + '\r\n'
        header += 'Accept: */*\r\n'
        header += 'Content-Length: ' + str(bodyLen) + '\r\n'
        header += 'Content-Type:application/x-www-form-urlencoded \r\n'
        header += 'Connection: close\r\n'
        header += '\r\n'
	
	# add body if there is one	
        if(bodyLen > 0):
            header += body
	    header += '\r\n'

	# connect and send request
        connection = self.connect(url.hostname, url.port)
	connection.send(header)
	response = self.recvall(connection)
	
	# extract code and body from response	
        code = int(self.get_code(response))
        body = self.get_body(response)

        return HTTPRequest(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1], command )    
