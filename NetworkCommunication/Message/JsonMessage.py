import json

from Message.ByteMessage import ByteMessage


class JsonMessage(ByteMessage):
    CONTENT_TYPE = 'text/json'

    def __init__(self, content):
        super().__init__(content, self.CONTENT_TYPE, 'utf-8')

    @staticmethod
    def decode_message(content, content_encoding):
        data = content.decode(content_encoding)
        content = json.loads(data, encoding=content_encoding)
        return JsonMessage(content)

    def encode_content_as_bytes(self, content, content_encoding):
        return json.dumps(content, ensure_ascii=True).\
            encode(encoding=content_encoding)
