"""
SERVER SIDE
This code is used to receive, route, & respond to messages.
It does not manipulate any data. The manipulation is done 
in the library ATM_Lib2
"""
import socketserver
import configparser
from xml.dom.minidom import parse
import xml.dom.minidom
import sys

from ATM_Constants import *
from ATM_Classes import *
from ATM_XML import *
from ATM_Lib2 import *

my_debugTCP = False    #debug print flag
#
# https://docs.python.org/3.8/library/socketserver.html 
# https://realpython.com/python-sockets/
#
class MyTCPHandler(socketserver.BaseRequestHandler):
    """
    The request handler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        if my_debugTCP:
            print("{} wrote:".format(self.client_address[0]))
            print(self.data)
        
        # Extract message ID
        if doesTagExist(self.data, XML_MESSAGE_ID):
            messageID = getTagContent(self.data, XML_MESSAGE_ID)
        else:
            messageID = FAILED

        if my_debugTCP:
            print('received messageID=',messageID)

        return_msg = ''
        # Determine what to with the message
        if messageID == STOP_APP:
            return_msg = stop_server()
        elif messageID == TEST_MESSAGE:
            return_msg = TestConnection_resp()
        elif messageID == VALIDATE_PIN:
            return_msg = ValidatePIN_resp(self.data)
        elif messageID == GET_CASH:
            pass
        # Default message: Unidentified message
        else:
            return_msg = messageID()
        
        # send back the response
        self.request.sendall(return_msg)

        # shutdown the server
        if messageID == STOP_APP:
            if my_debugTCP:
                print('Server shutdown issued')
            server.shutdown()
            server.server_close()
#
## read server_config.ini
parser = configparser.ConfigParser()
parser.read('server_config.ini') 

"""
TCP/IP code taken from Python.org
https://docs.python.org/3.8/library/socketserver.html
"""
HOST = parser['setup']['tcpip_hostname']
PORT = int(parser['setup']['tcpip_port'])
if my_debugTCP:
    print('section=',parser.sections())
    print('Host=', HOST)
    print('Port=', PORT)

if __name__ == "__main__":
#    HOST, PORT = "localhost", 1234

    # Create the server, binding to localhost on port xxxx
    server = socketserver.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print('Ctrl+C to end the server program')
    server.serve_forever()