import json
import struct
import socket

from Message.ByteMessage import ByteMessage
from Message.Message import Message
from Message.MessageParser import MessageParser


class MessageIO:
    def __init__(self, socket_connection: socket):
        self.socket_connection = socket_connection

    def read_next_message(self, message_parsers: MessageParser) -> ByteMessage:
        header_length = struct.unpack('>H', self.socket_connection.read(2))[0]
        header = json.loads(self.socket_connection.read(header_length).decode(Message.DEFAULT_ENCODING))
        content_length = header[Message.HEADER_CONTENT_LENGTH]
        content = self.socket_connection.read(content_length)
        return message_parsers.parse(header, content)

    def send_message(self, message: Message):
        self.socket_connection.sendall(message.to_bytes())
