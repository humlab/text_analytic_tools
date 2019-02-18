import re
from bs4 import BeautifulSoup, SoupStrainer
import datetime
from papacy_scraper.items import PapalTextItem

class PapalTextItemParser:  

    @staticmethod
    def textify(html):
        xml = BeautifulSoup(html, "html.parser")
        for x in xml.find_all("p", { 'align': 'center' }):
            x.decompose()
        for x in xml.find_all("center"):
            x.decompose()
        text = xml.get_text("\n")
        text = text.replace(u'\xa0', u' ')
        text = re.sub(r'(\n+)+', r'\n', text)
        return text

    @staticmethod
    def get_date(url):
        try:
            x = re.search("(?P<date>\d{8})", url)
            return datetime.datetime.strptime(x.group('date'), "%Y%m%d") if x != None else None
        except:
            return None
    
    @staticmethod
    def create_basename(item):
        return '{0}_{1}_{2}_{3}{4}_{5}'.format(item['pope'], item['lang'], item['type'],
            int(item['year'] or (item['date'] and item['date'].year) or 0),
            '_' + item['spec'] if item['spec'] else '', item['base'].replace('_','-'))

    @staticmethod
    def parse(response):

        item = PapalTextItem()

        m = re.search(r'/content/(?P<pope>[\w-]+)/(?P<lang>en|it|fr|es|la|pl|pt)/(?P<type>\w+)/(?P<year>\d{4})?(?:/)?(?P<spec>.*)?(?:/)?documents/(?P<base>.+)\.html$', response.url)

        if not m: raise Exception("Unable to decode url {0}".format(response.url))

        item['url'] = response.url
        item['pope'] = m.group('pope')
        item['lang'] = m.group('lang')
        item['type'] = m.group('type')
        item['spec'] = m.group('spec')
        item['year'] = m.group('year')
        item['base'] = m.group('base')
        item['html'] = response.xpath('//div[contains(@class, "documento")]').extract_first()
        item['text'] = PapalTextItemParser.textify(item["html"])
        item['date'] = PapalTextItemParser.get_date(response.url)
        item['filebase'] = PapalTextItemParser.create_basename(item)

        return item