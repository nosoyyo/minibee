import os
import json
import time
import redis
import requests
from bs4 import BeautifulSoup

from .exceptions import BumbleBeeError
from .utils import GeneralResp, slowDown, sigmaActions


class AbstractBee():
    '''
    Gerenralized crawler. Must contain `cpool` if not `site_obj` for redis.

    :method _SOUP: return BeautifulSoup(resp.text)
    :method _DOWNLOAD: return bytes or save file_name to local storage.
    '''

    def __init__(self, site_obj=None, _session=None, cpool=None):

        if site_obj:
            self.cpool = site_obj.cpool
            self.cookies = site_obj.cookies
            self.headers = site_obj.headers
        elif _session:
            self.cpool = cpool
            self.cookies = _session.cookies
            self.headers = _session.headers
        else:
            self.cpool = redis.ConnectionPool(host='localhost',
                                    port=6379,
                                    decode_responses=True,
                                    db=0)
            self.cookies = {}
            self.headers = {}
        self.r = redis.Redis(connection_pool=self.cpool)
        self.s = _session or requests.Session()

    # TODO
    def detectCookiesExpire(self):
        pass

    def add_cookies(self, _dict):
        try:
            self.s.cookies.update(_dict)
            return True
        except Exception:
            return False

    @slowDown
    def _GET(self,
             url: str,
             headers={},
             _params: dict = None,
             **kwargs) -> dict:
        '''
        :param _params: <dict>
        '''
        resp = None
        headers = headers or self.headers.copy()
        ua = 'User-Agent'
        if not headers[ua] or not headers[ua.lower()]:
            headers[ua] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        _params = _params or {}

        try:
            occur = time.time()
            resp = self.s.get(url, cookies=self.cookies,
                              headers=headers, params=_params)
        except Exception as e:
            print(f'some {e} happens during _GET')
        finally:
            sigmaActions(self.r, occur)

        if 'file' in kwargs:
            return resp.content
        else:
            return GeneralResp(resp)

    @slowDown
    def _POST(self, url: str, headers=None, _data=None, _params=None):
        '''
        :return ?: may return a `dict` or an `int` as http code

        :param _data: <dict> the data that requests.post needs.
        '''

        headers = headers or self.headers.copy()

        content_type = {'Content-Type': 'application/json;charset=UTF-8'}
        headers.update(content_type)
        print(f"Content-Type: {headers['Content-Type']}")

        _data = _data or {}
        _params = _params or {}

        try:
            resp = self.s.post(url, cookies=self.cookies,
                               headers=headers, json=_data, params=_params)
            return GeneralResp(resp)
        except Exception:
            raise BumbleBeeError()
        finally:
            sigmaActions(self.r, time.time())

    @slowDown
    def _DELETE(self, url: str) -> str:
        raise NotImplementedError

    @slowDown
    def _PUT(self, url: str) -> str:
        raise NotImplementedError

    def _XGET(self, url: str, _params: dict = None, **kwargs) -> dict:
        '''
        :param _params: <dict>
        '''
        if 'headers' in kwargs:
            headers = kwargs['headers']
        else:
            headers = self.headers.copy()
        x = {'X-Requested-With': 'XMLHttpRequest'}
        accept = {'Accept': 'application/json, text/plain, */*'}
        headers.update(accept)
        headers.update(x)
        resp = self._GET(url, _params=_params, headers=headers)

        return GeneralResp(resp)

    def _SOUP(self, url: str):
        print(f'cooking soup from {url}...')
        resp = self._GET(url)
        if resp:
            print('soup ready.')
            return BeautifulSoup(resp._content.decode(), 'lxml')

    def _DOWNLOAD(self, url: str, file_name=None):
        '''
        use this method to download files

        :param file_name: return binary content if None
        '''
        started = time.time()
        resp = self._GET(url, file=True)
        if not file_name:
            return resp
        else:
            with open(file_name, 'wb') as f:
                f.write(resp)
            print(f'{file_name} downloaded from {url}')

            # stats
            usage = time.time() - started
            size = os.path.getsize(file_name)
            print(f'{size} bytes, {usage:.1f} seconds. \n\
{size / usage / 1024:.1f} kb/s')
