
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
import os

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

    data = '\
Airbus says it has turned the corner after a crisis connected to production problems and turmoil in the boardroom at its A380 super-jumbo project that has gone on for the past year. Speaking at the Paris air show, Louis Gallois, CEO of the European planemaker, said, \"Airbus is back.\"\
Airbus, which announced a raft of orders on the first day of the show, is competing with Boeing, its American rival, for the title of the largest planemaker in the world.\
Boeing is expected to reveal the numbers of orders for its 787 Dreamliner soon. Airbus orders unveiled on Monday included Qatar Airways confirming a $16bn order for 80 A350 Airbus planes and ordering three A380 super-jumbos for about $750m.\
Boeing and Airbus are also competing for orders from aircraft leasing firms. Orders from these companies - who rank highly among the biggest global buyers of aircraft - are often regarded as an indication of how successful a model will be in the long term.\
Airbus also secured orders from US Airways that are worth $10bn for 22 of its A350 jets, 60 A320s and ten of its A330-200 wide-body planes.\
A few months ago, Airbus unveiled a major cost-cutting programme aiming to reduce the workforce in Europe by 10,000, as well as announcing a group restructuring. \"I can tell you with full confidence that Airbus is back and fully back, as you have started noting yesterday as demonstrated by our\ first day announcements,\" said Mr Gallois on the second day of the air show. \
However, Boeing also announced a deal with General Electric (GE) on the show\'s first day. GE\'s commercial aviation services placed an order for six 777 Boeing freighters valued at around $1.4bn, to be delivered in the last quarter of 2008.\
A Wall Street Journal website report, quoting the Delta operating chief yesterday said that Delta Air Lines were on the verge of ordering as many as 125 Boeing 787 jetliners by the end of this year. However, a spokesman for Delta later said that it had been having conversations \"with several\ aircraft makers\" and that \"no final decision\" had been made on future fleet purchases.\
'

    from papacy_scraper.pos_tagger import POSTaggerService, XMLTransformService
    tagger = POSTaggerService()
    output = tagger.tag(data)
    transformer = XMLTranslateService()
    xml = transformer.transform(output[0])

    print(transformer.as_string(xml))

    def get_project_dir():  
        return os.path.dirname(os.path.realpath(__file__))

    os.chdir(get_project_dir())

    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl('papalcrawlspider')
    process.start()
    #self.crawler.stop()

