
# class VaticanSpider(scrapy.Spider):

#     name = 'francisspider'

#     def __init__(self, options):
#         self.options = options

#     def content_root(self):
#         return "/content/{0}/{1}/".format(self.options['pope'], self.options['language'])

#     def start_requests(self):

#         # pope = getattr(self, 'pope', None) # usage: -a pope=francesco

#         domain_name = self.options['domain']
#         allowed_domains = [ self.options['domain'] ]
#         urls = [
#             'http://w2.vatican.va{0}.html'.format(self.content_root())
#         ]

#         for url in urls:
#             yield scrapy.Request(url, self.parse_pope)

#     def get_link_page_meta_data(self, link):
#         '''
#         Extracts document type and year from link as a tuple
#         Link must match pattern /content/nnnn/en/zzzz/yyyy.index.html or /content/nnnn/en/zzzz.index.html
#         where nnnn is popes name, zzzz is document type and yyyy is year
#         '''
#         link = link[link.index('/content'):]
#         m = re.match(r"(/content/(?P<pope>\w+)/(?P<lang>\w{2}))/(?P<type>\w+)(?P<subtype>[/]pont-messages)*(?P<year>[/][0-9]{4})*", link)
#         return {
#             'pope': m.group('pope'),
#             'lang': m.group('lang'),
#             'type': m.group('type'),
#             'subtype': m.group('type'),
#             'year': m.group('year'),
#             'link': link
#         } if m else None

#     def parse_pope(self, response):
#         '''
#         Extracts all links from accordion menu for current pope, extracts pope, type, language and year from link
#         '''
#         items = [ self.get_link_page_meta_data(x) for x in response.css('#accordionmenu li:not(.has-sub) a[href*="' + self.content_root() + '"]::attr(href)').extract() ]
#         items = [ x for x in items if not x is None and x['type'] in self.options['document_types'] ]

#         for item in items:
#             yield scrapy.Request(response.urljoin(item['link']), meta={'item': item}, callback=self.parse_link_page)

#     def parse_link_page(self, response):
            
#         item = response.meta['item']

#         links_selector = "/content/{0}/{1}/".format(item['pope'], item['lang'])
#         text_links = response.css('div.vaticanindex ul a[href*="' + links_selector + '"]::attr(href)').extract()

#         for link in text_links:
#             yield scrapy.Request(response.urljoin(link),  meta={'item': item}, callback=self.parse_text_page)

#         forward_link = response.css('#corpo div.vaticanindex__navigation a.btn.btn--nav[title="Forward"]').extract_first()
#         if forward_link is not None:
#             yield scrapy.Request(response.urljoin(forward_link), callback=self.parse_link_page)
 
#     def parse_text_page(self, response):

#         text = ''.join(BeautifulSoup(str(response.css('#corpo div.documento div.testo').extract())).findAll(text=True))

#         yield {
#             'text': text
#         }
 
# if __name__ == "__main__":

#     options = {
#         'domain': 'vatican.va',
#         'pope': 'francesco',
#         'language': 'en',
#         'document_types': ['angelus', 'audiences', 'speeches', 'travels', 'cotidie', 'travels', 'letters', 'messages', 'homilies', 'elezione']
#     }

#     configure_logging({'LOG_FORMAT': '%(levelname)s: %(message)s'})
#     runner = CrawlerRunner()

#     d = runner.crawl(VaticanSpider, options=options)
#     d.addBoth(lambda _: reactor.stop())
#     reactor.run() 