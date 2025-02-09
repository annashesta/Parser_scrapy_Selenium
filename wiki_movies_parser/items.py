# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WikiMoviesParserItem(scrapy.Item):
    title = scrapy.Field()  # Название фильма
    genre = scrapy.Field()  # Жанр фильма
    director = scrapy.Field()  # Режиссер фильма
    country = scrapy.Field()  # Страна производства
    year = scrapy.Field()  # Год выпуска
    imdb_id = scrapy.Field()  # ID IMDb
    imdb_rating = scrapy.Field()  # Рейтинг IMDb


