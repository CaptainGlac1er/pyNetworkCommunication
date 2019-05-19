import ssl
import socket
from threading import Thread, Lock

from Message.ByteMessage import ByteMessage
from Message.JsonMessage import JsonMessage
from Message.MessageIO import MessageIO
from Message.MessageParser import MessageParser


class Client(Thread):
    def __init__(self, hostname, port, ca_cert):
        Thread.__init__(self)
        self.hostname = hostname
        self.port = port
        self.socket_lock = Lock()
        self.ssock = None
        self.ca_cert = ca_cert

    def run(self):
        with self.socket_lock:
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            context.load_verify_locations(self.ca_cert)
            print("client: connecting")
            sock = socket.create_connection((self.hostname, self.port))
            self.ssock = context.wrap_socket(sock, server_hostname=self.hostname)
            Thread(target=self.server_listener, args=(self.ssock, )).start()

    def send_message(self, message: ByteMessage):
        with self.socket_lock:
            byte_stream = message.to_bytes()
            print(f'Client: sending -> {byte_stream}')
            self.ssock.sendall(byte_stream)

    def server_listener(self, socket):
        with self.socket_lock:
            pass
        message_connection = MessageIO(
            socket_connection=socket,
            message_parsers=MessageParser([ByteMessage, JsonMessage]))
        while True:
            print(f'{"Client:":>10s} is listening for next message')
            message = message_connection.read_next_message()
            print(f'{"Client:":>10s} received "{message.get_content()}"')

    def close(self):
        self.ssock.close()
