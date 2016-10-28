import json

import requests

# from http.cookiejar import LWPCookieJar

__all__ = ['session']

COOKIE_FILE = 'data/cookies-my.json'  # change this to cookies.json


def load_cookies():
    with open(COOKIE_FILE) as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError as e:
            raise SystemExit('Cookie file parse failed: ' + e.msg)


session = requests.Session()

# s.cookies = LWPCookieJar('cookies.txt')
# s.cookies.load(ignore_discard=True, ignore_expires=True)

session.headers['User-Agent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/54.0.2840.71 Safari/537.36')

session.cookies.update(load_cookies())
