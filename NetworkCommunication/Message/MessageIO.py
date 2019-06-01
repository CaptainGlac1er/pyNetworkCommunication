import json
import struct
import socket
import threading
from typing import Optional

from Message.ByteMessage import ByteMessage
from Message.Message import Message
from Message.MessageParser import MessageParser


class MessageIO:
    MAX_DATA_READ = 1024

    def __init__(self, socket_connection: socket, socket_connection_lock: threading.Lock = None):
        self.socket_connection: socket = socket_connection
        self.socket_connection_lock = socket_connection_lock

    def read_next_message(self, message_parsers: MessageParser) -> Optional[ByteMessage]:
        try:
            data = self.socket_connection.recv(2)
        except Exception as e:
            return None
        if not data:
            return None
        with self.socket_connection_lock:
            header_length = struct.unpack('>H', data)[0]
            header = json.loads(self.socket_connection.recv(header_length).decode(Message.DEFAULT_ENCODING))
            content_length = header[Message.HEADER_CONTENT_LENGTH]
            b_content = []
            data_transferred = 0
            while data_transferred < content_length:
                b_content.append(self.socket_connection.recv(min(content_length - data_transferred, self.MAX_DATA_READ)))
                data_transferred += len(b_content[-1])
        content = b''.join(b_content)
        return message_parsers.parse(header, content)

    def send_message(self, message: Message) -> bool:
        try:
            with self.socket_connection_lock:
                self.socket_connection.sendall(message.to_bytes())
            return True
        except Exception as e:
            return False
