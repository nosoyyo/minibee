__doc__ = '2to3 by nosoyyo'
__version__ = '2c376'

# Copyright 2014 Baidu, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
#  use this file
# except in compliance with the License. You may obtain a copy of the License
#  at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
# OF ANY KIND,
# either express or implied. See the License for the specific language
# governing permissions
# and limitations under the License.

"""
This module provide some tools for bce client.
"""

import re
import datetime
import hashlib
import base64
import string
import urllib.parse
from Crypto.Cipher import AES

from . import protocol
from . import http_headers


DEFAULT_ENCODING = "UTF-8"


def get_md5_from_fp(fp, offset=0, length=-1, buf_size=8192):
    """
    Get MD5 from file by fp.

    :type fp: FileIO
    :param fp: None

    :type offset: long
    :param offset: None

    :type length: long
    :param length: None
    =======================
    :return:
        **file_size, MD(encode by base64)**
    """

    origin_offset = fp.tell()
    if offset:
        fp.seek(offset)
    md5 = hashlib.md5()
    while True:
        bytes_to_read = buf_size
        if bytes_to_read > length > 0:
            bytes_to_read = length
        buf = fp.read(bytes_to_read)
        if not buf:
            break
        md5.update(buf)
        if length > 0:
            length -= len(buf)
        if length == 0:
            break
    fp.seek(origin_offset)
    return base64.standard_b64encode(md5.digest()).decode()


def get_canonical_time(timestamp=0):
    """
    Get cannonical time.

    :type timestamp: int
    :param timestamp: None
    =======================
    :return:
        **string of canonical_time**
    """
    if isinstance(timestamp, str):
        return timestamp
    elif timestamp == 0:
        utctime = datetime.datetime.utcnow()
    else:
        utctime = datetime.datetime.utcfromtimestamp(timestamp)
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (
        utctime.year, utctime.month, utctime.day,
        utctime.hour, utctime.minute, utctime.second)


def is_ip(s):
    """
    Check a string whether is a legal IPv4 address.

    :type s: string
    :param s: None
    =======================
    :return:
        **Boolean**
    """
    try:
        tmp_list = s.split(':')
        s = tmp_list[0]
        if s == 'localhost':
            return True
        tmp_list = s.split('.')
        if len(tmp_list) != 4:
            return False
        else:
            for i in tmp_list:
                if int(i) < 0 or int(i) > 255:
                    return False
    except Exception as e:
        return False
    return True


def convert_to_standard_string(input_string):
    """
    Encode a string to utf-8.

    :type input_string: string
    :param input_string: None
    =======================
    :return:
        **string**
    """
    if isinstance(input_string, str):
        return input_string
    else:
        return str(input_string)


def convert_header2map(header_list):
    """
    Transfer a header list to dict

    :type s: list
    :param s: None
    =======================
    :return:
        **dict**
    """
    header_map = {}
    for a, b in header_list:
        if isinstance(a, str):
            a = a.strip('\"')
        if isinstance(b, str):
            b = b.strip('\"')
        header_map[a] = b
    return header_map


def safe_get_element(name, container):
    """
    Get element from dict which the lower of key and name are equal.

    :type name: string
    :param name: None

    :type container: dict
    :param container: None
    =======================
    :return:
        **Value**
    """
    for k, v in list(container.items()):
        if k.strip().lower() == name.strip().lower():
            return v
    return ""


def check_redirect(res):
    """
    Check whether the response is redirect.

    :type res: HttpResponse
    :param res: None

    :return:
        **Boolean**
    """
    is_redirect = False
    try:
        if res.status == 301 or res.status == 302:
            is_redirect = True
    except Exception as e:
        pass
    return is_redirect


def _get_normalized_char_list():
    ret = ['%%%02X' % i for i in range(256)]
    for ch in string.ascii_letters + string.digits + '.~-_':
        ret[ord(ch)] = ch
    return ret


_NORMALIZED_CHAR_LIST = _get_normalized_char_list()


def normalize_string(in_str, encoding_slash=True):
    """
    i.e. UriEncode()
    Encode in_str.
    When encoding_slash is True, don't encode skip_chars, vice versa.

    :type in_str: string
    :param in_str: None

    :type encoding_slash: Bool
    :param encoding_slash: None
    ===============================
    :return:
        **string**
    """
    tmp = []
    for ch in convert_to_standard_string(in_str):
        if ch == '/' and not encoding_slash:
            tmp.append('/')
        else:
            tmp.append(_NORMALIZED_CHAR_LIST[ord(ch)])
    return ''.join(tmp)


def append_uri(base_uri, *path_components):
    """
    Append path_components to the end of base_uri in order,
    and ignore all empty strings and None

    :param base_uri: None
    :type base_uri: string

    :param path_components: None

    :return: the final url
    :rtype: str
    """
    tmp = [base_uri]
    for path in path_components:
        if path:
            tmp.append(normalize_string(path, False))
    if len(tmp) > 1:
        tmp[0] = tmp[0].rstrip('/')
        tmp[-1] = tmp[-1].lstrip('/')
        for i in range(1, len(tmp) - 1):
            tmp[i] = tmp[i].strip('/')
    return '/'.join(tmp)


def check_bucket_valid(bucket):
    """
    Check bucket name whether is legal.

    :type bucket: string
    :param bucket: None
    =======================
    :return:
        **Boolean**
    """
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789-"
    if len(bucket) < 3 or len(bucket) > 63:
        return False
    if bucket[-1] == "-" or bucket[-1] == "_":
        return False
    if not (('a' <= bucket[0] <= 'z') or ('0' <= bucket[0] <= '9')):
        return False
    for i in bucket:
        if i not in alphabet:
            return False
    return True


_first_cap_regex = re.compile('(.)([A-Z][a-z]+)')
_number_cap_regex = re.compile('([a-z])([0-9]{2,})')
_end_cap_regex = re.compile('([a-z0-9])([A-Z])')


def pythonize_name(name):
    """Convert camel case to a "pythonic" name.
    Examples::
        pythonize_name('CamelCase') -> 'camel_case'
        pythonize_name('already_pythonized') -> 'already_pythonized'
        pythonize_name('HTTPRequest') -> 'http_request'
        pythonize_name('HTTPStatus200Ok') -> 'http_status_200_ok'
        pythonize_name('UPPER') -> 'upper'
        pythonize_name('ContentMd5')->'content_md5'
        pythonize_name('') -> ''
    """
    if name == "eTag":
        return "etag"
    s1 = _first_cap_regex.sub(r'\1_\2', name)
    s2 = _number_cap_regex.sub(r'\1_\2', s1)
    return _end_cap_regex.sub(r'\1_\2', s2).lower()


def get_canonical_querystring(params, for_signature):
    """

    :param params:
    :param for_signature:
    :return:
    """
    if params is None:
        return ''
    result = []
    for k, v in list(params.items()):
        if not for_signature or k.lower != http_headers.AUTHORIZATION.lower():
            if v is None:
                v = ''
            result.append('%s=%s' % (normalize_string(k), normalize_string(v)))
    result.sort()
    return '&'.join(result)


def print_object(obj):
    """

    :param obj:
    :return:
    """
    tmp = []
    for k, v in list(obj.__dict__.items()):
        if not k.startswith('__'):
            if isinstance(v, str):
                tmp.append("%s:'%s'" % (k, v))
            elif isinstance(v, str):
                tmp.append("%s:u'%s'" % (k, v))
            else:
                tmp.append('%s:%s' % (k, v))
    return '{%s}' % ','.join(tmp)


'''
class Expando(object):
    """
    Expandable class
    """

    def __init__(self, attr_dict=None):
        if attr_dict:
            self.__dict__.update(attr_dict)

    def __getattr__(self, item):
        if item.startswith('__'):
            raise AttributeError
        return None

    def __repr__(self):
        return print_object(self)
'''


class SelfAssemblingClass():
    def __init__(self, doc=None):
        if doc:
            self.__dict__ = doc


class Expando(SelfAssemblingClass):
    pass


def dict_to_python_object(d):
    """

    :param d:
    :return:
    """
    attr = {}
    for k, v in list(d.items()):
        k = pythonize_name(str(k))
        attr[k] = v
    return Expando(attr)


def required(**types):
    """
    decorator of input param check
    :param types:
    :return:
    """
    def _required(f):
        def _decorated(*args, **kwds):
            for i, v in enumerate(args):
                if f.__code__.co_varnames[i] in types:
                    if v is None:
                        raise ValueError('arg "%s" should not be None' %
                                         (f.__code__.co_varnames[i]))
                    if not isinstance(v, types[f.__code__.co_varnames[i]]):
                        raise TypeError('arg "%s"= %r does not match %s' %
                                        (f.__code__.co_varnames[i],
                                         v,
                                         types[f.__code__.co_varnames[i]]))
            for k, v in kwds.items():
                if k in types:
                    if v is None:
                        raise ValueError('arg "%s" should not be None' % k)
                    if not isinstance(v, types[k]):
                        raise TypeError(
                            f'arg "{k}"= {v} does not match {types[k]}')
            return f(*args, **kwds)
        _decorated.__name__ = f.__name__
        return _decorated
    return _required


def parse_host_port(endpoint, default_protocol):
    """
    parse protocol, host, port from endpoint in config

    :type: string
    :param endpoint: endpoint in config

    :type: baidubce.protocol.HTTP or baidubce.protocol.HTTPS
    :param default_protocol: if there is no scheme in endpoint,
                              we will use this protocol as default
    :return: tuple of protocol, host, port
    """
    # netloc should begin with // according to RFC1808
    if "//" not in endpoint:
        endpoint = "//" + endpoint

    try:
        # scheme in endpoint dominates input default_protocol
        parse_result = urllib.parse.urlparse(endpoint, default_protocol.name)
    except Exception as e:
        raise ValueError('Invalid endpoint:%s, error:%s' %
                         (endpoint, e.message))

    if parse_result.scheme == protocol.HTTP.name:
        _protocol = protocol.HTTP
        port = protocol.HTTP.default_port
    elif parse_result.scheme == protocol.HTTPS.name:
        _protocol = protocol.HTTPS
        port = protocol.HTTPS.default_port
    else:
        raise ValueError('Unsupported protocol %s' % parse_result.scheme)
    host = parse_result.hostname
    if parse_result.port is not None:
        port = parse_result.port

    return _protocol, host, port


def aes128_encrypt_16char_key(adminpass, secretkey):
    """
    encrypt admin password by AES128
    """
    def pad_it(s): return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
    key = secretkey[0:16]
    mode = AES.MODE_ECB
    cryptor = AES.new(key, mode, key)
    cipheradminpass = cryptor.encrypt(pad_it(adminpass)).encode('hex')
    return cipheradminpass
