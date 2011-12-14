#!/usr/bin/python

from distutils.core import setup

from wessex import __version__

setup(name="Wessex",
      version=__version__,
      description="Client library for Harold",
      author="Neil Williams",
      author_email="neil@reddit.com",
      url="http://github.com/spladug/wessex",
      py_modules = ["wessex"])
