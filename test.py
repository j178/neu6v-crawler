import json

import requests

# from http.cookiejar import LWPCookieJar

WATER_ZONE_URL = 'http://bt.neu6.edu.cn/forum-4-1.html'
COOKIE_FILE = 'cookies-my.json' # change this to cookies.json


def load_cookies():
    with open(COOKIE_FILE) as f:
        try:
            return json.load(f)
        except json.decoder.JSONDecodeError as e:
            raise SystemExit('Cookie file parse failed: ' + e.msg)


s = requests.Session()

# s.cookies = LWPCookieJar('cookies.txt')
# s.cookies.load(ignore_discard=True, ignore_expires=True)

s.headers['User-Agent'] = ('Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.71 Safari/537.36')

s.cookies.update(load_cookies())

if __name__ == '__main__':

    rsp = s.get(WATER_ZONE_URL)

    # s.cookies.save(ignore_discard=True, ignore_expires=True)

    if '开心灌水' in rsp.text:
        print('登录成功')

    with open('index.html', 'w') as f:
        f.write(rsp.text)
