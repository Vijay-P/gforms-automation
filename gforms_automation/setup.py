'''
My DOCSTRING
'''

from codecs import open as c_open
from os import path
from setuptools import setup

here = path.abspath(path.dirname(__file__))

with c_open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='gforms_automation',
    version='1.0a1',
    description='A Python3 module that uses Selenium to provide a programmatic interface to Google Forms',
    author='Vijay Pillai',
    author_email='vijay@vijaypillai.com',
    py_modules=["gform.py"],
    install_requires=['selenium']
)
