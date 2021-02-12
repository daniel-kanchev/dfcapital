import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from dfcapital.items import Article


class DfSpider(scrapy.Spider):
    name = 'df'
    start_urls = ['https://www.dfcapital.co.uk/news/']

    def parse(self, response):
        articles = response.xpath('//div[@class="media_list"]/div')
        for article in articles:
            link = article.xpath('.//a/@href').get()
            date = article.xpath('.//div[@class="media_date"]//text()').get().strip()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

    def parse_article(self, response, date):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2[@class="post-title"]/text()').get()
        if title:
            title = title.strip()

        date = date.split()
        date[0] = date[0][:-2]
        date = " ".join(date)
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')

        content = response.xpath('//article[@id="content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
