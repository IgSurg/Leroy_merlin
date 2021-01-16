
import scrapy
from scrapy.http import HtmlResponse
from leroy_merlin.items import LeroyMerlinItem
from scrapy.loader import ItemLoader



class LeroyTheSpiderSpider(scrapy.Spider):
    name = 'leroyspider'
    allowed_domains = ['leroymerlin.ru']

    def __init__(self, search,search2,search3):
        super(LeroyTheSpiderSpider, self).__init__()
        self.start_urls = [f'https://leroymerlin.ru/search/?q={search}',f'https://leroymerlin.ru/search/?q={search2}',f'https://leroymerlin.ru/search/?q={search3}']

    def parse(self, response:HtmlResponse):
        links_list = response.xpath("//a[@class='plp-item__info__title']")
        for link in links_list:
            yield response.follow(link, callback=self.carpet_parse)
        next_page = response.xpath("//a[contains(@class, 'next-paginator-button')]/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def carpet_parse(self, response:HtmlResponse):
        loader = ItemLoader(item=LeroyMerlinItem(), response=response)
        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('images', "//source[contains(@media, '1024px')]/@srcset")  # Все изображения на сайте имею несколько расширений и 1024
        loader.add_xpath('info_key', "//dl/div/dt/text()")                          #
        loader.add_xpath('info_item', "//dl/div/dd/text()")
        loader.add_xpath('price', "//span[@slot='price']/text()")
        loader.add_xpath('_id', "//span[@slot='article']/text()")
        loader.add_value('link', response.url)
        yield loader.load_item()

