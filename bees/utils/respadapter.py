__doc__ = 'for adapting 3 main types of resp: requests, baidubce & bumblebee'
import json
from requests import Response as RequestsResponse

from .bce import BceResponse
from .sac import SelfAssemblingClass


class GeneralResp():
    '''

    0. if everything is ok, directly access this for json
    1. if something wrong, giving out the raw resp for debugging
        thus: not isinstance(this, dict)
    '''

    def __new__(self, resp):
        '''
        :param resp: one of the three type of resps
        '''

        if isinstance(resp, SelfAssemblingClass) or isinstance(resp,
                                                               GeneralResp):
            return resp
        elif isinstance(resp, BceResponse):
            print(f'assebmling a BceResponse .obj..')
            return SelfAssemblingClass(resp.metadata.__dict__)
        elif isinstance(resp, RequestsResponse):
            print(f'assembling a requests.Response obj...')
            try:
                doc = json.loads(resp.content)
                print('doc seems ok, pass it for assembling...')
                return SelfAssemblingClass(doc)
            except Exception:
                print('assembling a requests.Response')
                return SelfAssemblingClass(resp.__dict__)
        else:
            print(
                f'respadapter.GeneralResp: input must be some Response <obj>,\
                     got a {type(resp)}')

    def __contains__(self, item):
        return item in self.__dict__.keys()
