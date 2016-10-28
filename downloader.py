import json
import re
from urllib.parse import urljoin

from crawler import BeautifulSoup
from session import session as s


def atoi(s):
    num = re.search(r'^\d+', s)
    if num:
        return int(num.group())
    return 0


INDEX_PAGE = 'http://bt.neu6.edu.cn/plugin.php?id=neubt_resourceindex'

downloaded = set()


def load():
    global downloaded
    with open('downloaded.json') as f:
        try:
            l = json.load(f)
        except json.JSONDecodeError:
            return
        downloaded = set(l)


def save():
    with open('downloaded.json', 'w') as f:
        json.dump(list(downloaded), f)


def get_new():
    r = s.get(INDEX_PAGE)
    r.raise_for_status()

    soup = BeautifulSoup(r.text)

    for thread in soup.find('div', id='threadlist').find_all('tr'):
        size = thread.find_all('td')[2].text
        href = thread.find_all('td')[3].a['href']

        if (size.endswith('GB') and atoi(size) > 50) or size.endswith('TB'):
            continue

        url = urljoin(INDEX_PAGE, href)
        if url not in downloaded:
            yield url


def download(url):
    # 进入资源页面
    r = s.get(url)
    soup = BeautifulSoup(r.text)
    a = soup.find('dl', class_='tattl').a
    # 获取种子下载链接
    href = a['href']
    name = a.text
    print(name, href)
    if not href:
        return

    # 直接下载种子或者进入待下载页面
    r = s.get(urljoin(url, href))
    r.raise_for_status()
    print(r.headers)

    # 直接下载
    if 'Content-Disposition' in r.headers and r.headers['Content-Type'] == 'application/x-bittorrent':
        print('直接下载')
        filename = re.findall(r'filename="(.+)"', r.headers['Content-Disposition'])[0]
        content = r.content
    else:
        soup = BeautifulSoup(r.text)
        torrent_url = soup.find('p', class_='alert_btnleft').a['href']
        r = s.get(urljoin(url, torrent_url))
        r.raise_for_status()

        print(r.headers)
        filename = re.findall(r'filename="(.+)"', r.headers['Content-Disposition'])[0]
        content = r.content

    with open(filename, 'wb') as f:
        f.write(content)

    downloaded.add(url)


def main():
    load()
    for url in get_new():
        print('new', url)
        download(url)
    save()


def test():
    download('http://bt.neu6.edu.cn/thread-1563666-1-1.html')


if __name__ == '__main__':
    test()
