# -*- coding: utf-8 -*-
import os, io
from scrapy.exceptions import DropItem
from papacy_scraper.items import PapalTextItem
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize
from pos_tagger import POSTaggerService
import logging

class SaveItemService():

    @staticmethod
    def write(folder, filename, ext, data):
        filename = os.path.join(folder, '{0}.{1}'.format(filename, ext))
        with io.open(filename,'w',encoding='utf8') as f:
            f.write(text)
        logging.info('Stored item as {0} in {1}'.format(ext.upper(),filename))

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

        SaveItemService.write(spider.output_folder, item['filebase'], 'txt', item['text'])

        return item

class StanfordTaggerItemPipeline(object):

    tagger = POSTaggerService()

    def process_item(self, item, spider):

        if not 'text' in item:
            raise DropItem('Warning: Item has no text')

        item['pos_text'] = StanfordTaggerItemPipeline.tagger.tag(item['text'])

        SaveItemService.write(spider.output_folder, item['filebase'], 'xml', item['pos_text'])

        return item