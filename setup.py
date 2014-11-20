#!/usr/bin/python

from setuptools import setup

from wessex import __version__

setup(name="Wessex",
      version=__version__,
      description="Client library for Harold",
      author="Neil Williams",
      author_email="neil@reddit.com",
      url="http://github.com/spladug/wessex",
      py_modules = ["wessex"],
      install_requires=[
          "requests",
      ],
      entry_points={
          "console_scripts": [
              "harold-irc = wessex:harold_irc",
          ]
      }
 )
