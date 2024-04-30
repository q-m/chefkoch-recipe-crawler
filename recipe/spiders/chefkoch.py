import json
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from ..util import text, html, strip_hash_qs, apply_priority


class ChefkochSpider(CrawlSpider):
    name = 'chefkoch'
    allowed_domains = ['chefkoch.de']
    start_urls = ['https://www.chefkoch.de/rezepte/']

    rules = (
        # category pages
        Rule(
            LinkExtractor(allow=(r'/rs/s\d+/'))
        ),
        # recipes
        Rule(
            LinkExtractor(
                allow=(r'www\.chefkoch\.de/rezepte/\d+'),
                # Clean up URLs parts for tracking, as this pollutes the cache and could give duplicates.
                # - hash is often included for tracking the session
                # - query string may be present for tracking plus recipe traffic source
                process_value=strip_hash_qs,
                # omit plus recipes, for which we have no access
                restrict_css='*:not([data-vars-payed-content-type=plus_recipe]) > a'
            ),
            callback='parse_recipe',
            process_request=apply_priority(10)
        )
    )

    def parse_recipe(self, response):
        return {
            'url': response.url,
            'url_fingerprint': self.crawler.request_fingerprinter.fingerprint(response.request).hex(),
            'name': text(response.css('h1::text').get()),
            'image_url': response.css('meta[property="og:image"]::attr(content)').get(),
            'description': html(response.css('.recipe-text').get()),
            'preparation_time': text(response.css('.recipe-preptime::text').get()),
            'difficulty': text(response.css('.recipe-difficulty::text').get()),
            'date': text(response.css('.recipe-date::text').get()),
            'rating_avg': text(response.css('.ds-rating-avg strong').get()),
            'rating_count': text(response.css('.ds-rating-count > span > span:not(.rds-only)').get()),
            'comment_count': text(response.css('.rds-comment-ctn-btn strong').get()),
            'author_name': text(response.css('.recipe-author .bi-profile::attr(data-vars-bi-username)').get()),
            'author_url': response.css('.recipe-author .bi-profile::attr(href)').get(),
            'portions': response.css('.recipe-servings input[name=portionen]::attr(value)').get(),
            'ingredients': self.extract_ingredients(response),
            'preparation': self.extract_preparation(response),
            'durations': self.extract_durations(response),
            'tags': self.extract_tags(response),
        }

    def extract_ingredients(self, response):
        ingredients = []
        section = None
        for row in response.css('.ingredients tr'):
            if row.css('th'):
                s = text(row.css('th').get())
                if s: s = s.strip(':')
                if s != '':
                    section = s
                continue
            ingredients.append({
                'section': section,
                'amount': text(row.css('td:first-child').get()),
                'name': text(row.css('td:last-child').get()),
                'url': row.css('td:last-child .bi-recipe-ingredient-link::attr(href)').get()
            })
        return ingredients

    def extract_preparation(self, response):
        steps = response.css('h2:contains("Zubereitung") + .ds-recipe-meta + .ds-box *::text').getall()
        steps = [s.strip() for s in steps]
        steps = [s for s in steps if s != '']
        return steps

    def extract_durations(self, response):
        durations = {}
        for line in response.css('.ds-box > .ds-recipe-meta > *::text').getall():
            parts = line.strip().split(' ', 1)
            if len(parts) == 2:
                durations[parts[0]] = parts[1]
        return durations

    def extract_tags(self, response):
        tags = response.css('.recipe-tags .ds-tag').getall()
        tags = [text(s) for s in tags]
        return tags



