import json
import logging
import struct
import socket
import threading
from typing import Optional, Union

from Message.ByteMessage import ByteMessage
from Message.Message import Message
from Message.MessageParser import MessageParser


class MessageIO:
    MAX_DATA_READ = 1024
    TIMEOUT = 5

    def __init__(self, socket_connection: socket):
        self.socket_connection: socket = socket_connection
        self.socket_lock: threading.Lock = threading.Lock()

    def read_next_message(self, message_parsers: MessageParser) -> Optional[Union[ByteMessage, bool]]:
        try:
            data = self.socket_connection.recv(2)
        except Exception as e:
            return None
        if not data:
            return False
        header_length = struct.unpack('>H', data)[0]
        data_received = b''
        try:
            while len(data_received) < header_length:
                self.socket_connection.settimeout(self.TIMEOUT)
                read_count = min(header_length - len(data_received), self.MAX_DATA_READ)
                data_received += self.socket_connection.recv(read_count)
                self.socket_connection.settimeout(None)
        except socket.timeout as e:
            logging.error(f'{"MessageIO: ":>10s} message header timed out')
            return False
        logging.debug(data_received)
        header = json.loads(data_received.decode(Message.DEFAULT_ENCODING))
        content_length = header[Message.HEADER_CONTENT_LENGTH]
        content = b''
        try:
            while len(content) < content_length:
                self.socket_connection.settimeout(self.TIMEOUT)
                read_count = min(content_length - len(content), self.MAX_DATA_READ)
                content += self.socket_connection.recv(read_count)
                self.socket_connection.settimeout(None)
        except socket.timeout as e:
            logging.error(f'{"MessageIO: ":>10s} message content timed out')
            return False
        return message_parsers.parse(header, content)

    def send_message(self, message: Message) -> bool:
        try:
            with self.socket_lock:
                self.socket_connection.sendall(message.to_bytes())
            return True
        except Exception as e:
            return False
