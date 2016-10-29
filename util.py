import json
import os


def load_config(file, attempt=None):
    """
    First attempt to load from the attempt, otherwise from the file.
    If attempt not specified, default adding '.mine' to file. (a.mine.json)
    """
    if attempt is None:
        base, ext = os.path.splitext(file)
        attempt = ''.join([base, '.mine', ext])

    if os.path.isfile(attempt):
        file = attempt

    with open(file) as f:
        return json.load(f)
