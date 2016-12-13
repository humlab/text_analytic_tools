import re
from bs4 import BeautifulSoup
import datetime
from papacy_scraper.items import PapalTextItem

class PapalTextItemParser:    

    @staticmethod
    def textify(html):
        return re.sub(r'(\n+)+', r'\n', BeautifulSoup(html or "", "lxml").get_text("\n").replace(u'\xa0', u' '))

    @staticmethod
    def get_date(url):
        try:
            x = re.search("(?P<date>\d{8})", url)
            return datetime.datetime.strptime(x.group('date'), "%Y%m%d") if x != None else None
        except:
            return None
    '''
    http://w2.vatican.va/content/francesco/en/angelus/2016/documents/papa-francesco_angelus_20161127.html
    http://w2.vatican.va/content/francesco/en/apost_constitutions/documents/papa-francesco_costituzione-ap_20160629_vultum-dei-quaerere.html
    http://w2.vatican.va/content/francesco/en/apost_letters/documents/papa-francesco-lettera-ap_20160817_humanam-progressionem.html
    http://w2.vatican.va/content/francesco/en/audiences/2016/documents/papa-francesco_20161130_udienza-generale.html
    http://w2.vatican.va/content/francesco/en/bulls/documents/papa-francesco_bolla_20150411_misericordiae-vultus.html
    http://w2.vatican.va/content/francesco/en/encyclicals/documents/papa-francesco_20150524_enciclica-laudato-si.html
    http://w2.vatican.va/content/francesco/en/homilies/2016/documents/papa-francesco_20161119_omelia-concistoro-nuovi-cardinali.html
    http://w2.vatican.va/content/francesco/en/letters/2016/documents/papa-francesco_20160815_chirografo-mons-paglia.html
    http://w2.vatican.va/content/francesco/en/messages/communications/documents/papa-francesco_20160124_messaggio-comunicazioni-sociali.html
    http://w2.vatican.va/content/francesco/en/motu_proprio/documents/papa-francesco_20160817_statuto-dicastero-servizio-sviluppo-umano-integrale.html
    http://w2.vatican.va/content/francesco/en/prayers/documents/papa-francesco_preghiere_20151208_giubileo-straordinario-misericordia.html
    http://w2.vatican.va/content/francesco/en/speeches/2013/december/documents/papa-francesco_20131221_auguri-curia-romana.html
    http://w2.vatican.va/content/francesco/en/speeches/2013/december/documents/papa-francesco_20131221_auguri-curia-romana.html
    http://w2.vatican.va/content/francesco/en/travels/2016/inside/documents/papa-francesco-assisi-giornata-preghiera-pace_2016.html
    http://w2.vatican.va/content/francesco/en/travels/2015/outside/documents/papa-francesco-africa-2015.html
    http://w2.vatican.va/content/francesco/en/cotidie/2014/documents/papa-francesco-cotidie_20141219_the-time-of-re-creation.html
    '''

    @staticmethod
    def parse(response):

        item = PapalTextItem()

        m = re.search(r'/content/'\
                       '(?P<pope>\w+)/'\
                       '(?P<lang>(en|it|fr|es|la|pl|pt))/'\
                       '(?P<type>\w+)/'\
                       '((?P<year>\d{4})/)?'\
                       '((?P<spec>(.*))/)?'\
                       '(documents/)'\
                       '(?P<base>.+)\.html', response.url)

        if not m:
            raise Exception("Unable to decode url {0}".format(response.url))

        item['url'] = response.url
        
        item['pope'] = m.group('pope'),
        item['lang'] = m.group('lang'),
        item['type'] = m.group('type'),
        item['spec'] = m.group('spec'),
        item['year'] = m.group('year')
        item['base'] = m.group('base')

        item['html'] = response.xpath('//div[contains(@class, "documento")]').extract_first()
        item['text'] = PapalTextItemParser.textify(item["html"])
        item['date'] = PapalTextItemParser.get_date(response.url)

        return item