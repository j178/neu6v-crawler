import json
import os
import re
import sys
import logging
from urllib.parse import urljoin

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

log = logging.getLogger('downloader')
logging.basicConfig(level=logging.DEBUG)

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
    if 'Content-Disposition' in r.headers and r.headers['Content-Type'] == 'application/x-bittorrent':
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

        print(r.headers)
        filename = get_filename_from_response(r)
        log.debug('Downloading torrent file {}'.format(filename))
        content = r.content

    downloaded.add(url)

    return filename, content


def main():
    load()
    for url in get_new():
        print('new', url)
        filename, content = download(url)
        utorrent.add_file(bytes=content)
    save()


def load_config():
    with open(CONFIG_FILE) as f:
        return json.load(f)


if __name__ == '__main__':
    utorrent = uTorrent(**load_config())
    main()
    # test()
