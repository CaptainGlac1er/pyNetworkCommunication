import json

from Message.Message import Message
from Message.ByteMessage import ByteMessage


class JsonMessage(ByteMessage):
    CONTENT_TYPE = 'text/json'

    def __init__(self, content, custom_headers=None, encoding='utf-8'):
        super().__init__(content, custom_headers, self.CONTENT_TYPE, encoding)

    @staticmethod
    def decode_message(content, headers):
        content_encoding = headers[Message.HEADER_CONTENT_ENCODING]
        data = content.decode(content_encoding)
        content = json.loads(data, encoding=content_encoding)
        return JsonMessage(content, custom_headers=headers, encoding=content_encoding)

    def encode_content_as_bytes(self):
        return json.dumps(self.content, ensure_ascii=True).\
            encode(encoding=self.content_encoding)
