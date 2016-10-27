import json
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup as _bs, NavigableString

BeautifulSoup = lambda x: _bs(x, 'lxml')

# from http.cookiejar import LWPCookieJar

WATER_ZONE_URL = 'http://bt.neu6.edu.cn/forum-4-1.html'
COOKIE_FILE = 'cookies-my.json'  # change this to cookies.json


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


def check_new_topic(html):
    soup = BeautifulSoup(html)
    for topic in soup.find_all('tbody', id=re.compile(r'^normalthread_(\d+)')):
        if topic.find('em').text == '[六维茶话]':
            a = topic.find('a', class_='s xst', style=None)
            if a:
                print(urljoin(WATER_ZONE_URL, a['href']), a.text)


def reply_new(b):
    """
    回复新主题
    :return:
    """


def reply_comment():
    """
    回复别人对我的评论
    :return:
    """


def main():
    rsp = s.get(WATER_ZONE_URL)

    # s.cookies.save(ignore_discard=True, ignore_expires=True)
    rsp.raise_for_status()

    if '开心灌水' in rsp.text:
        print('登录成功')

    check_new_topic(rsp.text)


def test_parse():
    with open('index.html', encoding='utf8') as f:
        check_new_topic(f.read())


if __name__ == '__main__':
    main()
