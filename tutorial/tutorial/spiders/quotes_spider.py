import scrapy


class QuotesSpider(scrapy.Spider):
    """docstring for ."""
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        # page = response.url.split('/')[-2]
        # filename = 'quotes-%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)
        # self.log('Saved file %s' % filename)
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
                'tags': quote.css('div.tags a.tag::text').extract(),
            }
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)


class QuotesSpider(scrapy.Spider):
    FEED_FORMAT = 'csv'
    FEED_EXPORT_FIELDS = ['authors', 'text']
    name = "author_quotes"

    def start_requests(self):
        url = 'http://quotes.toscrape.com/'
        tag = getattr(self, 'tag', None)
        if tag is not None:
            url = url + 'tag/' + tag
        yield scrapy.Request(url, self.parse)

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').extract_first(),
                'author': quote.css('small.author::text').extract_first(),
            }

        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, self.parse)


class RacesSpider(scrapy.Spider):
    FEED_FORMAT = 'csv'
    FEED_EXPORT_FIELDS = ['trac_name', 'start_race', 'race_id', 'horse_name', 'horse_id', 'horse_chances']
    name = "races"
    start_urls = ['https://www.betbright.com/horse-racing/today']
    
    def parse(self, response):
        "follow links to race pages"
        for href in response.css('div#selection_container_races_schedule table.racing tr td a.event_time::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href), callback=self.parse_race)

    def parse_race(self, response):
        "parsing race page"

        def extract_id():
            "extract race id"
            return response.css(
                'div#content_container div.inner_container ul::attr(data-event-id)'
                ).extract_first().strip()

        def list_filter(lst):
            "filter trash sp data -> ['sp', '45', 'sp', '87']"
            return [item for item in lst if item != 'SP']

        def list_to_string(lst):
            "alter list to string"
            return ''.join(lst)

        # base path for participants
        participant_base = response.css('li#racecard_'+extract_id()+'_tab_winmarket ul.horses-list')
        yield {
            'trac_name': list_to_string(
                response.css(
                    'div#content_container div.inner_container ul li.racecard-header div.event-name'
                    ).re(r'\s(\D+)<')
                ),
            'start_race': list_to_string(
                response.css(
                    'div#content_container div.inner_container ul li.racecard-header div.event-name'
                    ).re(r'(\d+:\d+)')
                ),
            'race_id': extract_id(),
            'horse_name': participant_base.css('li.horse-container ul.horse '
                +'li.horse-datafields-container ul.horse-datafields '
                +'li.horse-main-datafields-container ul.horse-main-datafields '
                +'li.field-information div.horse-information-righthand '
                +'div.horse-information-name::text').extract(),
            'horse_id': participant_base.css(
                'li.horse-container ul.horse::attr(data-participant-id)'
                ).extract(),
            'horse_chances': list_filter(participant_base.css(
                'li.horse-container ul.horse li.horse-datafields-container '
                +'ul.horse-datafields li.field-win-ew a.bet_now_btn::text').extract())
        }


class AuthorSpider(scrapy.Spider):
    name = 'author'

    start_urls = ['http://quotes.toscrape.com/']

    def parse(self, response):
        # follow links to author pages
        for href in response.css('.author + a::attr(href)').extract():
            yield scrapy.Request(response.urljoin(href),
                                 callback=self.parse_author)

        # follow pagination links
        next_page = response.css('li.next a::attr(href)').extract_first()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def parse_author(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        yield {
            'name': extract_with_css('h3.author-title::text'),
            'birthdate': extract_with_css('.author-born-date::text'),
            'bio': extract_with_css('.author-description::text'),
        }
