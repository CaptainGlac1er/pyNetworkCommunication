import ssl
import socket
from threading import Thread
from typing import Optional

from Client.ClientHandler import ClientHandler
from Message.ByteMessage import ByteMessage
from Message.JsonMessage import JsonMessage
from Message.MessageIO import MessageIO
from Message.MessageParser import MessageParser


class Client(object):
    def __init__(self, client_handler: ClientHandler, message_parsers=None):
        if message_parsers is None:
            message_parsers = [JsonMessage, ByteMessage]
        self.client_handler: ClientHandler = client_handler
        self.message_parser = MessageParser(message_parsers)
        self.connection = None
        self.message_io: Optional[MessageIO] = None

    def connect(self, hostname, port, ca_cert=None, secure_connection=True):
        print("client: connecting")
        sock = socket.create_connection((hostname, port))
        if secure_connection:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(ca_cert)
            self.connection = context.wrap_socket(sock, server_hostname=hostname)
        else:
            self.connection = sock
        self.client_handler.set_connection(self.connection)
        self.message_io = MessageIO(self.connection)
        Thread(target=self.server_listener).start()

    def send_message(self, message: ByteMessage):
        self.message_io.send_message(message)

    def server_listener(self):
        while True:
            message = self.message_io.read_next_message(self.message_parser)
            self.client_handler.process_message(message)

    def close(self):
        self.connection.close()
