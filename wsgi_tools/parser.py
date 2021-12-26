from json import loads, JSONDecodeError
from .error import HTTPException
import xml.etree.ElementTree as ET


class JSONParser:
    def __init__(self, app):
        self.app = app
        self.raw_content = None
        self.json_content = None

    def __call__(self, environ, start_response):
        if 'CONTENT_TYPE' in environ:
            if 'json' in environ['CONTENT_TYPE'].split('/')[1].split('+'):
                self.raw_content = environ['wsgi.input'].read(
                    int(environ.get('CONTENT_LENGTH', 0)))
                try:
                    self.json_content = loads(self.raw_content)
                except JSONDecodeError:
                    raise HTTPException(422, message='Invalid JSON')
                return self.app(environ, start_response)
            else:
                raise HTTPException(
                    415, message='Only json content is allowed.')
        else:
            raise HTTPException(400, message='Body required')


class XMLParser:
    def __init__(self, app):
        self.app = app
        self.raw_content = None
        self.root_element = None

    def __call__(self, environ, start_response):
        if 'CONTENT_TYPE' in environ:
            if 'xml' in environ['CONTENT_TYPE'].split('/')[1].split('+'):
                self.raw_content = environ['wsgi.input'].read(
                    int(environ.get('CONTENT_LENGTH', 0)))
                try:
                    self.root_element = ET.fromstring(self.raw_content)
                except ET.ParseError:
                    raise HTTPException(422, message='Invalid XML')
                return self.app(environ, start_response)
            else:
                raise HTTPException(
                    415, message='Only xml content is allowed.')
        else:
            raise HTTPException(400, message='Body required')
