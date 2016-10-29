import json

import requests
from util import load_config

# from http.cookiejar import LWPCookieJar

__all__ = ['session']

COOKIE_FILE = 'data/cookies.json'  # change this to cookies.json

session = requests.Session()

# s.cookies = LWPCookieJar('cookies.txt')
# s.cookies.load(ignore_discard=True, ignore_expires=True)

session.headers['User-Agent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/54.0.2840.71 Safari/537.36')

session.cookies.update(load_config(COOKIE_FILE))
