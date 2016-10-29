import logging
import re
from urllib.parse import urljoin

import requests


class uTorrent(object):
    def __init__(self, base_url, username, password):
        self.log = logging.getLogger(__name__)
        self.url = 'http://{}/gui/'.format(base_url)  # just base url
        self._session = requests.Session()
        self._session.auth = (username, password)
        self._token = None

    @property
    def token(self):
        if self._token is not None:
            return self._token

        self._token = self._get_token()
        return self._token

    def _get_token(self):
        token_url = urljoin(self.url, 'token.html')
        r = self._session.get(token_url)
        r.raise_for_status()

        token_regex = r'<div[^>]*id=[\"\']token[\"\'][^>]*>([^<]*)</div>'
        token = re.search(token_regex, r.text).group(1)
        self.log.info('Got uTorrent token {}'.format(token))
        return token

    def add_file(self, filepath=None, bytes=None):
        params = dict(action='add-file', token=self.token)

        if filepath is not None:
            filedata = open(filepath, 'rb')
        else:
            filedata = bytes

        files = dict(torrent_file=filedata)

        r = self._session.post(self.url, params=params, files=files)
        r.raise_for_status()

        self.log.info('Added file to uTorrent, got response {}'.format(r.text))
        return r.text
