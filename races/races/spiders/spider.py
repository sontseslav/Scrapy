import scrapy 


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
