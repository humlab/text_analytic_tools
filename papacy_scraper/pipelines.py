# -*- coding: utf-8 -*-
import os, io
from scrapy.exceptions import DropItem
from papacy_scraper.items import PapalTextItem
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
from papacy_scraper.pos_tagger import POSTaggerService, XMLTranslateService
import logging

class StoreTextService():

    @staticmethod
    def write(folder, filename, ext, data):
        filepath = os.path.join(folder, '{0}.{1}'.format(filename.replace('/','_'), ext))
        with io.open(filepath,'w',encoding='utf8') as f:
            f.write(data)
        logging.info('Stored item as {0} in {1}'.format(ext.upper(),filepath))

class StoreItemAsTextPipeline(object):

    def open_spider(self, spider):

        if not (spider.output_folder):
            raise Exception('Error: output folder is missing or invalid')

        if not os.path.exists(spider.output_folder):
            os.makedirs(spider.output_folder)

    def process_item(self, item, spider):

        if not (item and 'text' in item and item['text']):
            raise DropItem('No text in item')
        
        if not item['filebase']:
            raise DropItem('Error in filename or output folder')

        StoreTextService.write(spider.output_folder, item['filebase'], 'txt', item['text'])
        StoreTextService.write(spider.output_folder, item['filebase'], 'html', item['html'])

        return item

class StanfordTaggerItemPipeline(object):

    tagger = POSTaggerService()
    translator = XMLTranslateService()

    def process_item(self, item, spider):

        x = StanfordTaggerItemPipeline.tagger
        y = StanfordTaggerItemPipeline.translator

        if not 'text' in item:
            raise DropItem('Warning: Item has no text')

        xml = y.translate(x.tag(item['text'])[0])

        item['xml'] = xml

        StoreTextService.write(spider.output_folder, item['filebase'], 'xml', y.as_string(xml))

        return item