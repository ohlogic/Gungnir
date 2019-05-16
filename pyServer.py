#!/usr/bin/python3
#
# Copyright 2019 Stan S
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# You may contact Stan S via electronic mail with the address vfpro777@yahoo.com
#


# # given a pem file ... openssl req -new -x509 -keyout yourpemfile.pem -out yourpemfile.pem -days 365 -nodes

try:
    # For Python 3.0 and later
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from socketserver import ThreadingMixIn
except ImportError:
    # Fall back to Python 2's urllib2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
    from SocketServer import ThreadingMixIn

import threading
import argparse
import re
import cgi

from subprocess import PIPE, Popen, STDOUT

import ssl

# shell execute PHP
def PHP(code):
	p = Popen(['php'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)	#note: example set a 4th arg,  close_fds=True
	o = p.communicate(code.encode())[0]	# read output
	try:
		os.kill(p.pid, signal.SIGTERM)	# kill process
	except:
		pass
	return o

# shell execute python3
def PYTHON(code):
    p = Popen(['python3'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)	#note: example set a 4th arg,  close_fds=True
    o = p.communicate(code.encode())[0]	# read output
    try:
        os.kill(p.pid, signal.SIGTERM)	# kill process
    except:
        pass
    return o


class HTTPRequestHandler(BaseHTTPRequestHandler):
  
    # uncomment for bonus: GradeA+ SSLHandler
    def end_headers(self):
        self.send_header("Strict-Transport-Security", "max-age=63072000; includeSubDomains")
        BaseHTTPRequestHandler.end_headers(self)

    def do_POST(self):
        return

    def do_GET(self):    
        if self.path=="/":
            self.path="/index.php"

        
        try:
            #Check the file extension required and
            #set the right mime type

            sendReply = False
            if self.path.endswith(".php") or self.path.endswith(".py"):
                mimetype='text/html'
                sendReply = True
            
            if sendReply == True:
                #Open the dynamic, static file requested and send it
                f = open("." + self.path) 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                
                if self.path.endswith(".php"):        
                    self.wfile.write(PHP(f.read()))
                if self.path.endswith(".py"):        
                    self.wfile.write(PYTHON(f.read()))               
                else:
                    self.wfile.write(f.read())
                    
                f.close()
            return
                
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)
                    
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True

    def shutdown(self):
        self.socket.close()
        HTTPServer.shutdown(self)

class SimpleHttpServer():
    def __init__(self, ip, port):
        self.server = ThreadedHTTPServer((ip,port), HTTPRequestHandler)
    
        # https://www.sevenwatt.com/main/sslhttps-grade-a-python-simplehttpserver/
        # uncomment code block for a 'grade A' server with 100% scores
        #
        ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ctx.load_cert_chain(certfile="./yourpemfile.pem")
        ctx.options |= ssl.OP_NO_TLSv1
        ctx.options |= ssl.OP_NO_TLSv1_1
        ctx.options |= ssl.OP_CIPHER_SERVER_PREFERENCE
        ctx.set_ciphers('ECDHE-RSA-AES256-GCM-SHA384 ECDHE-RSA-AES256-SHA384 ECDHE-RSA-AES256-SHA')
        self.server.socket = ctx.wrap_socket(self.server.socket, server_side=True)

        # alternative: protocols at 100% grade, though leaves ciphers at 90% rating
        #self.server.socket = ssl.wrap_socket (self.server.socket, server_side=True,
        #                    certfile='./yourpemfile.pem', ssl_version=ssl.PROTOCOL_TLSv1_2)

    def start(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def waitForThread(self):
        self.server_thread.join()

    def stop(self):
        self.server.shutdown()
        self.waitForThread()

if __name__=='__main__':
      parser = argparse.ArgumentParser(description='HTTP Server')
      parser.add_argument('ip', help='HTTP Server IP')  
      parser.add_argument('port', type=int, help='Listening port for HTTP Server')

      args = parser.parse_args()

      server = SimpleHttpServer(args.ip, args.port)
      print ('HTTP Server Running...........')
      server.start()
      server.waitForThread()
