import logging
import ssl
import socket
import threading
from threading import Thread
from typing import Optional

from Client import ClientHandler
from Message import ByteMessage, JsonMessage, MessageIO, MessageParser


class Client(object):
    def __init__(self, client_handler: ClientHandler, message_parsers=None):
        if message_parsers is None:
            message_parsers = [JsonMessage, ByteMessage]
        self.client_handler: ClientHandler = client_handler
        self.message_parser = MessageParser(message_parsers)
        self.connection: Optional[socket] = None
        self.connection_open = False
        self.connection_lock = threading.Lock()
        self.message_io: Optional[MessageIO] = None

    def connect(self, hostname, port, ca_cert=None, secure_connection=True):
        print("client: connecting")
        with self.connection_lock:
            sock = socket.create_connection((hostname, port))
            if secure_connection:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations(ca_cert)
                self.connection = context.wrap_socket(sock, server_hostname=hostname)
            else:
                self.connection = sock
            self.connection_open = True
            self.client_handler.set_connection(self.connection)
            self.message_io = MessageIO(self.connection, self.connection_lock)
        Thread(target=self.server_listener).start()

    def send_message(self, message: ByteMessage):
        logging.debug(f'{"Client: ":>10s} sending message {message.get_hash()}')
        self.message_io.send_message(message)

    def server_listener(self):
        while self.connection_open:
            message_received = self.message_io.read_next_message(self.message_parser)
            if message_received:
                logging.debug(f'{"Client: ":>10s} received message {message_received.get_hash()}')
                self.client_handler.process_message(message_received)
            else:
                self.client_handler.connection_closed(self)
                break

    def close(self):
        with self.connection_lock:
            self.connection_open = False
            self.connection.close()
       # self.connection.shutdown(socket.SHUT_RDWR)
