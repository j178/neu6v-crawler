import json
import logging
import os
import re
import sys
import time
import traceback
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from crawler import BeautifulSoup
from session import session as s
from utorrent import uTorrent

INDEX_PAGE = 'http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex'
DOWNLOADED_FILE = 'data/record.json'
CONFIG_FILE = 'data/config-my.json'  # change this to data/config.json

# getLogger 时传入的name, 是为了日志分级, 默认返回 root, 在 Formatter中使用 %(name)s 可以获取logger的名字
# basicConfig是用来配置root logger的, 如果toot没有handler, 则生成一个, 如果已经有了则不做任何事
# getLogger() 或者 getLogger('') 都可以获取 root logger, 是一个单例, 默认的 level 是 Warning
# 如果一个logger没有显示的设置 Level, 则使用父logger的level, 一直到root logger
# 子logger收到消息之后, 也会传递给他所有的父logger
# 所以如果要看 requests 的日志, 只需要设置一下root的handler就好了, 因为requests的所有logger都是root的儿子, 最终都会传到root中来
# 库的作者一般都把logger的handler设为 NullHandler, 因为没有handler, 所以不会有任何输出

log = logging.getLogger()
hdlr = logging.FileHandler('v6.log', encoding='utf8')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

record = set()


def load():
    global record
    with open(DOWNLOADED_FILE) as f:
        log.info('Loading downloaded torrent files list from {}'.format(DOWNLOADED_FILE))
        l = json.load(f)
        record = set(l)


def save():
    with open(DOWNLOADED_FILE, 'w') as f:
        log.info('Saving new downloaded torrent files list')
        json.dump(list(record), f, indent=4)


def convert_size(s):
    """Convert the size string(12GB) to megabytes"""

    r = re.search(r'(\d+)\s+(.)B', s)
    if r:
        size = r.group(1)
        unit = r.group(2)
    else:
        raise ValueError('Invalid size: {!r}'.format(s))

    if unit == 'M':
        return int(size)
    if unit == 'G':
        return 1024 * int(size)
    if unit == 'T':
        return 1024 * 1024 * int(size)

    raise ValueError('Invalid size: {!r}'.format(s))


def fetch_new(filter=None):
    """Refresh the resource index page and yield new url that has not been recorded"""

    if filter is None:
        filter = lambda heat, size, is_free: size < 50 * 1024 and is_free and heat <= 3  # return True to be kept

    log.info('Fetching new thread from resource index page')
    r = s.get(INDEX_PAGE)
    r.raise_for_status()

    soup = BeautifulSoup(r.text)

    for thread in soup.find('div', id='threadlist').find_all('tr'):
        img = thread.find_all('td')[1].img
        heat = int(re.search(r'signal_(\d)\.png$', img['src']).group(1))

        try:
            size = convert_size(thread.find_all('td')[2].text)
        except ValueError as e:
            log.error(str(e))
            continue

        a = thread.find_all('td')[3].a
        href = a['href']
        title = a.text
        is_free = a.next_sibling is not None and a.next_sibling['src'].endswith('free.gif')

        url = urljoin(INDEX_PAGE, href)

        if not filter(heat, size, is_free):
            record.add(url)

        elif url not in record:
            log.info('Found new thread {} : {}'.format(title, href))
            record.add(url)
            yield url


def get_filename_from_response(r):
    return re.findall(r'filename="(.+)"', r.headers['Content-Disposition'], re.DOTALL)[0]


def download(url):
    """Go to the thread page and follow the link to download the torrent"""
    # 进入资源页面
    log.info('Going to resource page {}'.format(url))
    r = s.get(url)

    soup = BeautifulSoup(r.text)
    a = soup.find('dl', class_='tattl').a
    # 获取种子下载链接
    href = a['href']
    if not href:
        return
    log.info('Found torrent url: {}'.format(href))

    # 直接下载种子或者进入待下载页面
    r = s.get(urljoin(url, href))
    r.raise_for_status()

    # 直接下载
    if 'Content-Disposition' in r.headers:
        filename = get_filename_from_response(r)
        content = r.content
        log.info('Downloading torrent file {} directly'.format(filename))
    # 进入等待下载页面
    else:
        soup = BeautifulSoup(r.text)
        torrent_url = soup.find('p', class_='alert_btnleft').a['href']
        log.info('Going to the page waiting for downloading, torrent real url is {}'.format(torrent_url))
        r = s.get(urljoin(url, torrent_url))
        r.raise_for_status()

        filename = get_filename_from_response(r)
        log.info('Downloading torrent file {}'.format(filename))
        content = r.content

    return filename, content


def main():
    load()
    for url in fetch_new():
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
        log.error(traceback.format_exc())
        raise
        # test()
