#!/usr/bin/python

import sys, getopt
import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from run_options import PopeOptions

'''
Note: To run on windows do the following.
1. pip install scrapy
2. pip install pypiwin32
3. pip install twisted-win

precompiled (if VC is missing or wrong version):

    download Twister and Scrapy from http://www.lfd.uci.edu/~gohlke/pythonlibs/

    python -m pip install pip --upgrade
    pip install -U setuptools
    
    pip install Twisted-16.4.1-cp34-cp34m-win32.whl
    pip install Scrapy-1.2.0-py2.py3-none-any.whl

    pip install pypiwin32
    pip install twisted-win

    pip install beautifulsoup4 --upgrade

    # same procedure might be necessary for other dependent modules
'''

if __name__ == "__main__":

    def get_project_dir():  
        return os.path.dirname(os.path.realpath(__file__))

    os.chdir(get_project_dir())

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl('papalcrawlspider', options=PopeOptions)
    process.start()
    #self.crawler.stop()
