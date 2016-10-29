from downloader import *


def test_downloader():
    filename, content = download('http://bt.neu6.edu.cn/thread-1563637-1-1.html')
    print(filename)
    r = utorrent.add_file(bytes=content)
    print(r)


def test_convert_size():
    print(convert_size('1GB'))
    print(convert_size('100MB'))
    print(convert_size('1TB'))


if __name__ == '__main__':
    # test_downloader()#
    test_convert_size()
    pass
