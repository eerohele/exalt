import os

from os.path import expanduser
from urllib.request import pathname2url
from urllib.parse import urljoin
from collections import OrderedDict

import sublime
import sublime_plugin

import Markup.constants as constants
import Markup.settings as settings


class LimitedOrderedDict(OrderedDict):
    """An OrderedDict with a maximum size.

    Lifted from http://stackoverflow.com/a/2437645/825783."""
    def __init__(self, *args, **kwds):
        self.size_limit = kwds.pop("max_size", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


parser_cache = LimitedOrderedDict(max_size=10)
error_point = 0


def get_plugin_path():
    return os.path.dirname(os.path.normpath(os.path.abspath(__file__)))


def get_settings():
    settings_file = "%s.sublime-settings" % constants.PLUGIN_NAME
    return sublime.load_settings(settings_file)


def get_setting(key, default=None):
    return get_settings().get(key, default)


def get_catalog_files():
    # lxml uses the $XML_CATALOG_FILES environment variable to look for
    # XML catalog files, and since it's a bit tricky to set the variable
    # so that Sublime Text can see it on every platform, the user can add
    # their own catalog files in the plugin settings.
    catalog_files = get_setting(settings.XML_CATALOG_FILES)

    # Convert paths to URLs so that lxml can parse catalog paths with
    # spaces in them.
    catalog_urls = map(lambda s: urljoin("file:", pathname2url(expanduser(s))),
                       catalog_files)

    return " ".join(catalog_urls)


def reload_settings():
    settings = get_settings()
    settings.add_on_change(constants.PLUGIN_NAME, reload_settings)


def plugin_loaded():
    # The user needs to be able to set the location of their XML catalog files
    # in the .sublime-settings file of this plugin.
    #
    # Unfortunately, the XML_CATALOG_FILES environment variable must be set
    # *before* lxml is imported. The sublime.load_settings() method in turn
    # works only *after* plugins have finished loading.
    #
    # As a workaround, we'll wait until this plugin has finished loading and
    # only then load the files that import and use lxml.
    sublime_plugin.reload_plugin("%s.impl.plugin" % constants.PLUGIN_NAME)
    sublime_plugin.reload_plugin("%s.impl.validator" % constants.PLUGIN_NAME)


def plugin_unloaded():
    parser_cache.clear()
