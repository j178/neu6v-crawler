import json
import logging
import os
import re
import sys
from urllib.parse import urljoin

import time

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from crawler import BeautifulSoup
from session import session as s
from utorrent import uTorrent


def atoi(s):
    num = re.search(r'^\d+', s)
    if num:
        return int(num.group())
    return 0


INDEX_PAGE = 'http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex'
DOWNLOADED_FILE = 'data/downloaded.json'
CONFIG_FILE = 'data/config-my.json'  # change this to data/config.json

# getLogger 时传入的name, 是为了日志分级, 默认返回 root, 在 Formatter中使用 %(name)s 可以获取logger的名字
# basicConfig是用来配置root logger的, 如果toot没有handler, 则生成一个, 如果已经有了则不做任何事
# getLogger() 或者 getLogger('') 都可以获取 root logger, 是一个单例, 默认的 level 是 Warning
# 如果一个logger没有显示的设置 Level, 则使用父logger的level, 一直到root logger
# 子logger收到消息之后, 也会传递给他所有的父logger
# 所以如果要看 requests 的日志, 只需要设置一下root的handler就好了, 因为requests的所有logger都是root的儿子, 最终都会传到root中来
# 库的作者一般都把logger的handler设为 NullHandler, 因为没有handler, 所以不会有任何输出

log = logging.getLogger()
hdlr = logging.FileHandler('v6.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.DEBUG)

downloaded = set()


def load():
    global downloaded
    with open(DOWNLOADED_FILE) as f:
        log.debug('Loading downloaded torrent files list from {}'.format(DOWNLOADED_FILE))
        try:
            l = json.load(f)
        except json.JSONDecodeError:
            return
        downloaded = set(l)


def save():
    with open(DOWNLOADED_FILE, 'w') as f:
        log.debug('Saving new downloaded torrent files list')
        json.dump(list(downloaded), f)


def get_new():
    log.debug('Fetching new thread from resource index page')
    r = s.get(INDEX_PAGE)
    r.raise_for_status()

    soup = BeautifulSoup(r.text)

    for thread in soup.find('div', id='threadlist').find_all('tr'):
        size = thread.find_all('td')[2].text
        a = thread.find_all('td')[3].a
        href = a['href']
        title = a.text

        if (size.endswith('GB') and atoi(size) > 50) or size.endswith('TB'):
            continue

        url = urljoin(INDEX_PAGE, href)
        if url not in downloaded:
            log.debug('Found new thread {} : {}'.format(title, href))
            yield url


def get_filename_from_response(r):
    return re.findall(r'filename="(.+)"', r.headers['Content-Disposition'])[0]


def download(url, path=''):
    # 进入资源页面
    log.debug('Going to resource page {}'.format(url))
    r = s.get(url)
    soup = BeautifulSoup(r.text)
    a = soup.find('dl', class_='tattl').a
    # 获取种子下载链接
    href = a['href']
    log.debug('Found torrent url: {}'.format(href))
    if not href:
        return

    # 直接下载种子或者进入待下载页面
    r = s.get(urljoin(url, href))
    r.raise_for_status()

    # 直接下载
    if 'Content-Disposition' in r.headers:
        filename = get_filename_from_response(r)
        content = r.content
        log.debug('Downloading torrent file {} directly'.format(filename))
    # 进入等待下载页面
    else:
        soup = BeautifulSoup(r.text)
        torrent_url = soup.find('p', class_='alert_btnleft').a['href']
        log.debug('Going to the page waiting for downloading, torrent real url is {}'.format(torrent_url))
        r = s.get(urljoin(url, torrent_url))
        r.raise_for_status()

        filename = get_filename_from_response(r)
        log.debug('Downloading torrent file {}'.format(filename))
        content = r.content

    downloaded.add(url)

    return filename, content


def main():
    load()
    for url in get_new():
        filename, content = download(url)
        utorrent.add_file(bytes=content)
        time.sleep(5)
    save()


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


if __name__ == '__main__':
    utorrent = uTorrent(**load_config())
    try:
        main()
    except Exception as e:
        log.error(str(e))
        raise
        # test()
