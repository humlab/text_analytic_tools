import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from papacy_scraper.spiders.parser import PapalTextItemParser
import logging as log

class CrawlOptions(object):
    def __init__(self, pope, language, text_types, year=None):
        self.pope = pope
        self.language = language
        self.year = year
        self.target_domain = 'vatican.va'
        self.target_pope_root = "content/{0}/{1}".format(pope, language)

        '''Example: http://w2.vatican.va/content/francesco/en.html'''
        self.start_url = 'http://w2.{0}/{1}.html'.format(self.target_domain, self.target_pope_root)
        self.text_types = text_types

        self.navigation_link_patterns = [ '/{0}/{1}(.*)\.html'.format(self.target_pope_root, x) for x in self.text_types ]
        self.navigation_link_restrict_css = '#accordionmenu li:not(.has-sub)'

        '''Example: /content/francesco/en/letters/2016.index.2.html'''
        self.forward_link_pattern = '/{0}/(.*)\.index(\.\d*)*\.html'.format(self.target_pope_root)

        '''Example: /content/francesco/en/letters/2016/documents/papa-francesco_20160708_indipendenza-argentina.html'''
        self.document_link_pattern = '/{0}/(.*)/documents/(.*)\.html'.format(self.target_pope_root)

        self.deny_document_link_pattern = r'^(?!.*{}).*$'.format(year) if year is not None else None

class JobCrawlSpider(CrawlSpider):

    name = 'papalcrawlspider'

    def __init__(self, pope_options, *args, **kwargs):

        options = CrawlOptions(
            pope_options.pope,
            pope_options.lang,
            pope_options.categories,
            pope_options.year
        )

        self.output_folder = pope_options.output_folder
        self.start_urls = [ options.start_url ]
        self.allowed_domains = [ options.target_domain ]
        #self.deny_document = r'^(?!.*STRING1|.*STRING2|.*STRING3).*$'

        self.rules = [
            Rule(LinkExtractor(allow=options.navigation_link_patterns, restrict_css=options.navigation_link_restrict_css, unique=True), follow=True, callback='tree_link_callback'),
            Rule(LinkExtractor(allow=options.forward_link_pattern, restrict_css='.navigation-pages a[title="Forward"]', unique=True), follow=True, callback='forward_link_callback'),
            Rule(LinkExtractor(
                    allow=options.document_link_pattern,
                    deny=options.deny_document_link_pattern,
                    restrict_css='.documento',
                    unique=True
                ), follow=True, callback='document_link_callback')
        ]

        super(JobCrawlSpider, self).__init__(*args, **kwargs)

        self.options = options

    #def start_requests(self):
    #    return [ self.options.start_url ]

    def tree_link_callback(self, response):
        log.info("LINK PAGE FOUND: " + response.url)

    def forward_link_callback(self, response):
        log.info("FORWARD FOUND: " + response.url)

    def document_link_callback(self, response):
        log.info("DOCUMENT FOUND: " + response.url)
        yield PapalTextItemParser.parse(response)

    def closed(self, reason):
        log.info("{0} Closed: {1}".format(self.name,reason))
