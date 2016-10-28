from downloader import download, utorrent


def test_downloader():
    filename, content = download('http://bt.neu6.edu.cn/thread-1563637-1-1.html')
    print(filename)
    r = utorrent.add_file(bytes=content)
    print(r)


if __name__ == '__main__':
    test_downloader()
