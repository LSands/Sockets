# Sockets
client / server using sockets
The file TCP_server_test.py is the server-side app that receives an XML message, does something with it, and return data to the client.
The program works, and I have can test the socket connection and perform transactions.
Currently, the only way I can end the server app is to press Ctrl-C.
I would like to be able to send a message from the client 'STOP_APP' and shutdown / end the server side app. I can send in a STOP_APP
message, but the method 'server.shutdown()' doesn't seem to end the app. 
Any suggestions how to do this on the server-side?
