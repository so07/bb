#!/usr/bin/env python
from distutils.core import setup

import config

setup(

   name=config.name,
   version=config.version,
   description=config.description,
   author=config.author,
   author_email=config.author_email,
   url=config.url,
   data_files=['bb.py']

)
