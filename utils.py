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
