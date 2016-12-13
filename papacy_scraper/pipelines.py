# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
from papacy_scraper.items import PapalTextItem
from nltk.internals import find_jars_within_path
from nltk.tag import StanfordPOSTagger
from nltk import word_tokenize

import pprint
pp = pprint.PrettyPrinter(indent=4)

class StoreItemPipeline(object):

    def open_spider(self, spider):
        print("StoreItemPipeline.open_spider called")

    def close_spider(self, spider):
        """ Close DB connection """
        print("StoreItemPipeline.close_spider called")

    def process_item(self, item, spider):

        print("StoreItemPipeline.ProcessItem called")
        pp.pprint(item)

        return item


class StanfordTaggerItemPipeline(object):

    def open_spider(self, spider):
        print("StoreItemPipeline.open_spider called")

    def close_spider(self, spider):
        """ Close DB connection """
        print("StoreItemPipeline.close_spider called")

    def process_item(self, item, spider):

        print("StoreItemPipeline.ProcessItem called")

        jar = '\\usr\\stanford-postagger-full-2015-12-09\\stanford-postagger.jar'
        model = '\\usr\\stanford-postagger-full-2015-12-09\\models\\english-left3words-distsim.tagger'
        java_options = '-outputFormatOptions lemmatize '
        tagger = StanfordPOSTagger(model, jar)

        # Add other jars from Stanford directory
        stanford_dir = tagger._stanford_jar[0].rpartition('\\')[0]
        stanford_jars = find_jars_within_path(stanford_dir)
        tagger._stanford_jar = ':'.join(stanford_jars)

        text = tagger.tag(word_tokenize("What's the airspeed of an unladen swallow ?"))

        return item