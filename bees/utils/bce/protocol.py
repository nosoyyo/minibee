# Copyright 2014 Baidu, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file
# except in compliance with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the
# License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.
"""
This module defines constants that represent the communication protocol to use when sending requests to BCE.

Communication over HTTPS is the default, and is more secure than HTTP, which is why BCE recommends using HTTPS. HTTPS
connections can use more system resources because of the extra work to encrypt network traffic, so the option to use
HTTP is available in case users need it.
"""


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


HTTP = Expando({'name': 'http', 'default_port': 80})
HTTPS = Expando({'name': 'https', 'default_port': 443})
