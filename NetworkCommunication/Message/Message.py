import hashlib
import json
import struct
from datetime import datetime


class Message:
    DEFAULT_ENCODING = 'UTF-8'
    CONTENT_TYPE = 'bytes'
    HEADER_CONTENT_LENGTH = 'content-length'
    HEADER_CONTENT_ENCODING = 'content-encoding'
    HEADER_CONTENT_TYPE = 'content-type'
    HEADER_DATE = 'date'

    def __init__(self, content, custom_headers=None, content_type=CONTENT_TYPE, content_encoding=DEFAULT_ENCODING):
        if custom_headers is None:
            custom_headers = {}
        self.custom_headers = custom_headers
        self.content = content
        self.content_type = content_type
        self.content_encoding = content_encoding

    def encode_content_as_bytes(self) -> bytes:
        pass

    def decode_content(self, content, content_encoding):
        pass

    @staticmethod
    def decode_message(content, headers):
        pass

    def to_bytes(self):
        content_bytes = self.encode_content_as_bytes()
        headers = {
            Message.HEADER_CONTENT_LENGTH: len(content_bytes),
            Message.HEADER_CONTENT_TYPE: self.content_type,
            Message.HEADER_CONTENT_ENCODING: self.content_encoding,
            Message.HEADER_DATE: datetime.utcnow().isoformat()
        }
        headers.update(self.custom_headers)
        header_bytes = json.dumps(headers, ensure_ascii=True).encode(self.DEFAULT_ENCODING)
        message_header = struct.pack(">H", len(header_bytes))
        return message_header + header_bytes + content_bytes

    def get_content(self):
        return self.content

    def get_hash(self):
        return hashlib.sha3_512(self.encode_content_as_bytes()).hexdigest()
