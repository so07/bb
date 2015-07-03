#!/usr/bin/env python
from distutils.core import setup

from bb import config

setup(

   name=config.name,
   version=config.version,
   description=config.description,
   author=config.author,
   author_email=config.author_email,
   url=config.url,
   scripts=['bin/bb'],
   packages=['bb', 'bb/argconfig'],
   #data_files=['config.py']

)
