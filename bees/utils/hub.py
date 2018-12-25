__author__ = 'nosoyyo'
__version__ = '2c37c'

import os
import uuid
import base64
import requests
import numpy as np
from PIL import Image
from io import BytesIO


class ImageHubError(Exception):
    pass


class ImageHub():
    '''
    Awesome image operational tool for humans.
    '''

    DEFAULT_SIZE = (1024, 1289)
    VALID_FILETYPES = (
        '.jpg'
        '.jpeg'
        '.gif'
        '.png'
        '.webp'
        '.bmp'
    )

    def __init__(self, _input, size=None):

        self.image = self.convert(_input, to='PIL.Image')
        self._ndarray = self.convert(_input, to='np.ndarray')
        self._bytes = self.convert(_input, to='bytes')
        self._base64 = self.convert(_input, to='base64')

        self.width = len(self._ndarray[0])
        self.height = len(self._ndarray)
        self.size = (self.height, self.width)

    @classmethod
    def convert(self, _input, to='PIL.Image'):
        try:
            output = 'not ready yet'
            file_type = None
            is_file_name = False

            if isinstance(_input, ImageHub):
                hub = _input.image
            elif isinstance(_input, Image.Image):
                hub = _input
            elif isinstance(_input, np.ndarray):
                hub = Image.fromarray(_input)
            elif isinstance(_input, tuple):
                hub = Image.fromarray(_input)
            elif isinstance(_input, bytes):
                hub = Image.open(BytesIO(_input))
            elif isinstance(_input, str) and os.path.isfile(_input):
                hub = Image.open(_input)
                is_file_name = True
            elif self.is_valid_url(self, _input):
                is_file_name = True
                try:
                    _bytes = requests.get(_input).content
                    hub = Image.open(BytesIO(_bytes))
                except Exception:
                    raise ImageHubError('Image url not valid.')
            elif isinstance(_input, str) and _input.startswith('data:image/'):
                try:
                    if ',' in _input:
                        header = _input.split(',')[0]
                        _bytes = base64.b64decode(_input.replace(header, ''))
                    else:
                        _bytes = base64.b64decode(_input)
                    hub = Image.open(BytesIO(_bytes))
                except Exception:
                    raise ImageHubError('Invalid base64 encoding.')
            else:
                raise ImageHubError('Invalid input or type not supported.')

            if is_file_name:
                if _input.split('.')[-1] in self.VALID_FILETYPES:
                    file_type = _input.split('.')[-1]

            if not hub:
                return '_input not converted'
            elif to == 'PIL.Image':
                output = hub
            elif to == 'np.ndarray':
                output = np.array(hub)
            elif to == 'bytes':
                output = hub.tobytes()
            elif to == 'base64':
                if not file_type:
                    header = b'data:image/.+;base64,'
                else:
                    header = bytes(f'data:image/{file_type};base64,'.encode())
                data = base64.b64encode(hub.tobytes())
                output = header + data
            return output
        except Exception as e:
            print(e)

    def look(self, _input=None):
        img = _input or self.image
        self.convert(img, to='PIL.Image').show()

    @classmethod
    def invert(self, _input):
        _input = self.convert(_input, 'np.ndarray')
        for y in range(len(_input)):
            for x in range(len(_input[0])):
                _input[y][x] = abs(255-_input[y][x])
        return _input

    @classmethod
    def save(self, _input=None, filename: str = None, format='jpeg') -> str:
        _input = self.convert(_input, to='PIL.Image') or self.image

        def makeFilename(filename=None, format='jpeg'):
            if filename:
                suffix = filename.split('.')[-1]
            else:
                if format in ['jpg', 'jpeg']:
                    suffix = '.jpeg'
                elif format is 'png':
                    suffix = '.png'
            return uuid.uuid4().__str__() + suffix

        try:
            os.listdir('var/tmp/')
        except Exception:
            os.makedirs('var/tmp')

        if not filename:
            filename = 'var/tmp/' + makeFilename(format=format)

        _input.save(filename)
        return filename

    def addBleed(self,
                 size: tuple,
                 img=None,
                 color='black',
                 direction='vertical'
                 ):
        '''
        Add customized bleed piece on the given image.

        :return: ImageHub object

        :param img: <any> any image stuff. see ImageHub.__init__
        :param size: <tuple> target size,
                             not to confused with bleeding size
                             (width, height) looks like (1280,664)
        :param color: <str> or <int> # TODO
        :param direction: <str> `vertical` or `horizontal` # TODO

        '''
        bleeding = None
        img = img or self.image
        img = ImageHub(img).image

        if color == 'black':
            target = ImageHub.new(size=size).image
            bleeding = int((size[0] - img.width)/2)
            target.paste(img, (bleeding, 0, img.width + bleeding, img.height))
            temp = self.save(target)
            return ImageHub(temp)
        else:
            raise NotImplementedError

    def is_valid_url(self, _input):
        flag = False
        if isinstance(_input, str):
            if _input.startswith('http'):
                if _input.split('.')[-1] in self.VALID_FILETYPES:
                    flag = True
        return flag

    @classmethod
    def new(self, size=None):
        _size = size or self.DEFAULT_SIZE
        return ImageHub(Image.new('RGB', _size))

    def resize(self, size):
        return ImageHub(self.image.resize(size))
