import requests
from http.cookiejar import LWPCookieJar

WATER_ZONE_URL = 'http://bt.neu6.edu.cn/forum-4-1.html'

s = requests.Session()

# s.cookies = LWPCookieJar('cookies.txt')
# s.cookies.load(ignore_discard=True, ignore_expires=True)

s.headers[
    'User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 ' \
                    'Safari/537.36'

cookies = {
    'LRpW_2132_auth'   :
        '63b8VSiDLrL0t2V%2FR%2FM4zQU%2BAzOpj%2B2qNShWIhMXqEE57qhTgufHwtzHiz2kEayG453zn740I4WJpwx8vLonwVZocDk',
    'LRpW_2132_saltkey': 'GJJkJo4X',
}

s.cookies.update(cookies)

if __name__ == '__main__':

    rsp = s.get(WATER_ZONE_URL)

    # s.cookies.save(ignore_discard=True, ignore_expires=True)

    print(s.cookies)

    if '开心灌水' in rsp.text:
        print('登录成功')
