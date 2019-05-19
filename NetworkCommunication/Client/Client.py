import ssl
import socket
from threading import Thread, Lock

from Message.ByteMessage import ByteMessage


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
            print("client ready to send")

    def send_message(self, message: ByteMessage):
        with self.socket_lock:
            byte_stream = message.to_bytes()
            print(f'Client: sending -> {byte_stream}')
            self.ssock.sendall(byte_stream)

    def server_listener(self, socket):
        with self.socket_lock:
            pass

    def close(self):
        self.ssock.close()
