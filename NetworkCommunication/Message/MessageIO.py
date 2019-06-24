import io
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
    MAX_DATA_READ = 1000000
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
        data_received_len = 0
        try:
            received = io.BytesIO()
            self.socket_connection.settimeout(self.TIMEOUT)
            while data_received_len < header_length:
                read_count = min(header_length - data_received_len, self.MAX_DATA_READ)
                packet = self.socket_connection.recv(read_count)
                received.write(packet)
                data_received_len += len(packet)
            data_received = received.getbuffer().tobytes()
            received.close()
            self.socket_connection.settimeout(None)
        except socket.timeout as e:
            logging.error(f'{"MessageIO: ":>10s} message header timed out')
            return False
        logging.debug(data_received)
        header = json.loads(data_received.decode(Message.DEFAULT_ENCODING))
        content_length = header[Message.HEADER_CONTENT_LENGTH]
        data_received_len = 0
        try:
            received = io.BytesIO()
            self.socket_connection.settimeout(self.TIMEOUT)
            while data_received_len < content_length:
                read_count = min(content_length - data_received_len, self.MAX_DATA_READ)
                packet = self.socket_connection.recv(read_count)
                received.write(packet)
                data_received_len += len(packet)
            content = received.getbuffer().tobytes()
            received.close()
            self.socket_connection.settimeout(None)
        except socket.timeout as e:
            logging.error(f'{"MessageIO: ":>10s} message content timed out')
            return False
        return message_parsers.parse(header, content)

    def send_message(self, message: Message, delay=0) -> bool:
        try:
            with self.socket_lock:
                message_bytes = message.to_bytes()
                data_size = len(message_bytes)
                data_sent = 0
                while data_sent < data_size:
                    send_count = min(data_size - data_sent, self.MAX_DATA_READ)
                    self.socket_connection.send(message_bytes[data_sent:data_sent+send_count])
                    data_sent += send_count
            return True
        except Exception as e:
            return False
