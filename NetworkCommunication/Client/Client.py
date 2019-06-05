import logging
import ssl
import socket
import time
from threading import Thread, Lock
from typing import Optional

from Client import ClientHandler
from Message import ByteMessage, JsonMessage, MessageIO, MessageParser, Message


class Client(Thread):
    def __init__(self, client_handler: ClientHandler, hostname, port, ca_cert=None, secure_connection=True,
                 message_parsers=None, reconnect_delay=2):
        super().__init__()
        if message_parsers is None:
            message_parsers = [JsonMessage, ByteMessage]
        self.connection_state_lock: Lock = Lock()
        self.client_handler: ClientHandler = client_handler
        self.message_parser = MessageParser(message_parsers)
        self.connection: Optional[socket] = None
        self.connection_open = False
        self.connection_closed = False
        self.message_io: Optional[MessageIO] = None
        self.hostname = hostname
        self.port = port
        self.ca_cert = ca_cert
        self.secure_connection = secure_connection
        self.client_sender_thread: Optional[Thread] = None
        self.client_receiver_thread: Optional[Thread] = None
        self.reconnect_delay = reconnect_delay
        self.message_queue: [Message] = []

    def run(self):
        while not self.connection_closed:
            with self.connection_state_lock:
                if not self.connection_closed and not self.connection_open:
                    if self.connect():
                        break
            if not self.connection_open:
                time.sleep(self.reconnect_delay)
                logging.warning(f'{"Client: ":>10s} Retrying server')
        if self.connection_open:
            logging.info(f'{"Client: ":>10s} connected to server')
            logging.info(f'{"Client: ":>10s} starting client services')
            self.start_message_receiver()
            self.start_message_sender()
        else:
            logging.warning(f'{"Client: ":>10s} did not connect')


    def connect(self):
        self.connection_open = False
        logging.info(f'{"Client: ":>10s} Trying connecting to server')
        try:
            sock = socket.create_connection((self.hostname, self.port))
            logging.info(sock)
            if self.secure_connection:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
                context.load_verify_locations(self.ca_cert)
                self.connection = context.wrap_socket(sock, server_hostname=self.hostname)
            else:
                self.connection = sock
            self.client_handler.set_connection(self.connection)
            self.message_io = MessageIO(self.connection)
            self.connection_open = True
        except ConnectionRefusedError as e:
            return False
        return True

    def start_message_sender(self):
        if self.client_sender_thread is None or not self.client_sender_thread.is_alive():
            self.client_sender_thread = Thread(target=self.message_sender).start()

    def start_message_receiver(self):
        if self.client_receiver_thread is None or not self.client_receiver_thread.is_alive():
            self.client_receiver_thread = Thread(target=self.start_listener).start()

    def send_message(self, message: ByteMessage):
        logging.debug(f'{"Client: ":>10s} queuing message {message.get_hash()}')
        self.message_queue.append(message)
        self.start_message_sender()

    def is_connection_alive(self):
        with self.connection_state_lock:
            is_alive = not self.connection_closed and self.connection_open
        return is_alive

    def start_listener(self):
        logging.info(f'{"Client: ":>10s} Listening for messages')
        while self.is_connection_alive():
            message_received = self.message_io.read_next_message(self.message_parser)
            if message_received:
                logging.debug(f'{"Client: ":>10s} received message {message_received.get_hash()}')
                self.client_handler.process_message(message_received)
            else:
                self.client_handler.connection_closed(self)
                break

    def message_sender(self):
        while self.is_connection_alive() and len(self.message_queue) > 0:
            message_to_send = self.message_queue.pop()
            logging.debug(f'{"Client: ":>10s} sending message {message_to_send.get_hash()}')
            if not self.message_io.send_message(message_to_send):
                self.message_queue.append(message_to_send)
                logging.debug(f'{"Client: ":>10s} message failed to send, queued {message_to_send.get_hash()}')
                self.connect()
            logging.debug(f'{"Client: ":>10s} message sent')

    def close(self):
        with self.connection_state_lock:
            self.connection_closed = True
            if self.connection is not None:
                self.connection.shutdown(socket.SHUT_RDWR)
