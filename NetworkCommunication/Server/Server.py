import ssl
from socketserver import ThreadingMixIn, TCPServer
from threading import Thread

from Message.ByteMessage import ByteMessage
from Message.JsonMessage import JsonMessage
from Server.ServerClientConnectionFactory import ServerClientConnectionFactory


class Server(ThreadingMixIn, TCPServer, Thread):
    def __init__(self,
                 server_address,
                 router,
                 secure_connection=True,
                 certificate_file=None,
                 certificate_key_file=None,
                 ssl_version=ssl.PROTOCOL_TLS_SERVER,
                 ca_certs=None,
                 bind_and_activate=True,
                 message_parsers=None):
        if message_parsers is None:
            message_parsers = [JsonMessage, ByteMessage]
        handler = ServerClientConnectionFactory(router=router,
                                                message_parsers=message_parsers)
        Thread.__init__(self)
        TCPServer.__init__(self,
                           server_address=server_address,
                           RequestHandlerClass=handler.create_with_router,
                           bind_and_activate=bind_and_activate)
        self.ssl_version = ssl_version
        self.certificate_file = certificate_file
        self.certificate_key_file = certificate_key_file
        self.ca_certs = ca_certs
        self.secure_connection = secure_connection

    def get_request(self):
        new_socket, from_address = self.socket.accept()
        connection_stream = new_socket
        try:
            if self.secure_connection:
                connection_stream = ssl.wrap_socket(sock=new_socket,
                                                    server_side=True,
                                                    certfile=self.certificate_file,
                                                    keyfile=self.certificate_key_file,
                                                    ssl_version=self.ssl_version,
                                                    ca_certs=self.ca_certs)
        except ValueError:
            print("Server: ", "error -> ", ValueError)
        return connection_stream, from_address

    def run(self):
        print('Server running')
        self.serve_forever()
