import Exalt.encodings as encodings

import io
import os
from urllib.parse import urljoin, urlparse


def is_relative_path(url):
    u = urlparse(url)
    return not bool(u.scheme) and not bool(u.netloc) and not os.path.isabs(url)


def resolve_file_path(path, against):
    if against and is_relative_path(path):
        return urljoin("file:", urljoin(against, path))
    else:
        return path


def string_to_bytes(string):
    # I have no idea whether this is the optimal way of parsing the
    # content of the view. If you try to parse it as a string, you'll
    # get the error described here:
    #
    # http://lxml.de/parsing.html#python-unicode-strings
    #
    # There's an lxml bug report on the subject that seems to suggest that
    # using BytesIO is the way to go:
    #
    # https://bugs.launchpad.net/lxml/+bug/613302
    #
    # But I feel that the documentation and the bug report conflict each
    # other to some extent. Improvement suggestions appreciated.
    return io.BytesIO(bytes(string, encodings.UTF8))
