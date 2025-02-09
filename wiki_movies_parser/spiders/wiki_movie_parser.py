# scrapy crawl wiki_movie_parser

import scrapy

class WikiMovieParserSpider(scrapy.Spider):
        name = "wiki_movie_parser"
        start_urls = ['https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту']
        allowed_domains = ["ru.wikipedia.org", "www.imdb.com"]


        def parse(self, response):
            """
            Обрабатывает страницу категории фильмов.
            Извлекает ссылки на фильмы и переходит на следующую страницу.
            """
            self.logger.info(f"Parsing category page: {response.url}")

            # Извлекаем ссылки на фильмы
            for movie in response.css("div.mw-category li"):
                link = movie.css("a::attr(href)").get()
                if link and "/wiki/" in link:  # Проверяем, что ссылка ведет на страницу фильма
                    yield response.follow(link, callback=self.parse_movie)

            # Ищем ссылку на следующую страницу
            next_page_link = response.css('#mw-pages a:contains("Следующая страница")::attr(href)').get()
            if next_page_link:
                self.logger.info(f"Found next page: {next_page_link}")
                yield response.follow(next_page_link, callback=self.parse)
            else:
                self.logger.info("No more pages to crawl.")

        def parse_movie(self, response):
            """
            Обрабатывает страницу фильма.
            Извлекает название, жанр, режиссера, страну, год выпуска и IMDb ID.
            """
            # Название фильма
            title = response.css("table.infobox th.infobox-above::text").get()
            if not title:
                title = response.css("#firstHeading::text").get()

            # Жанр фильма (учитываем варианты "Жанр" и "Жанры" благодаря contains(text(), 'Жанр'))
            genre = response.xpath("//*[contains(text(), 'Жанр')]/ancestor::tr//span/a/text()").getall()
            if not genre:
                genre = response.xpath("//*[contains(text(), 'Жанр')]/ancestor::tr//td/span/text()").getall()
            genre = ", ".join(genre)

            # Режиссер фильма (учитываем варианты "Режиссёр" и "Режиссёры")
            director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//span/a/text()").getall()
            if not director:
                director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//span/a/span/text()").getall()
            if not director:
                director = response.xpath("//*[contains(text(), 'Режиссёр')]/ancestor::tr//td/span/text()").getall()
            director = ", ".join(director)


            # Страна производства (учитываем варианты "Страна" и "Страны")
            country = response.xpath("//*[contains(text(), 'Стран')]/ancestor::tr//span/a/text()").get()
            if not country:
                country = response.xpath("//*[contains(text(), 'Стран')]/ancestor::tr//a/span/text()").getall()
                country = ', '.join(country)

            # Год выпуска (учитываем варианты "Год" и "Годы")
            year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td/a/span/text()").get()
            if not year:
                year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td/a/text()").get()
            if not year:
                year = response.xpath("//*[contains(text(), 'Год')]/ancestor::tr//td//span/a/text()").getall()
                year = ', '.join(year)

            # IMDb ID
            imdb_link = response.css('a[href*="imdb.com/title/"]::attr(href)').get()
            imdb_id = imdb_link.split("/")[-2] if imdb_link else None


            # Возвращаем данные
            movie =  {
                "title": title.strip() if title else None,
                "genre": genre,
                "director": director.strip() if director else None,
                "country": country.strip() if country else None,
                "year": year.strip() if year else None,
                "imdb_id": imdb_id.strip() if imdb_id else None,
                "imdb_rating": None,
            }

            yield movie

#             Далее была идея собрать рейтинг так же scrapy,
#             но сервер возвращал код 403 при попытке парсинга:
#
            # # 2025-02-09 09:59:04 [scrapy.core.engine] DEBUG:
            # Crawled (403) <GET https://www.imdb.com/title/tt1187043/>
            # (referer: https://ru.wikipedia.org/wiki/3_%D0%B8%D0%B4%D0%B8%D0%BE%D1%82%D0%B0)
            # 2025-02-09 09:59:04 [scrapy.spidermiddlewares.httperror]
            # INFO: Ignoring response <403 https://www.imdb.com/title/tt1187043/>: HTTP status code is not handled or not allowed


#       Вот такой был код, можно ли его как-то доработать, чтобы парсить рейтинг с помощью scrapy? :

            # Если есть ссылка на IMDB, то запускаем еще одного паука, чтобы вытащить рейтинг
        #
        #     if movie.get("imdb_id"):  # Проверяем, есть ли IMDb ID
        #         imdb_url = f"https://www.imdb.com/title/{movie['imdb_id']}/"
        #         print('imdb_url',imdb_url)
        #         yield scrapy.Request(imdb_url, callback=self.parse_imdb, meta={"movie": movie})
        #     else:
        #         # Если IMDb ID отсутствует, возвращаем данные с прочерком
        #         movie["imdb_rating"] = "-"
        #     yield movie
        #
        # def parse_imdb(self, response):
        #     """
        #     Обрабатываем страницу IMDb и извлекаем рейтинг.
        #     """
        #     movie = response.meta["movie"]
        #
        #     # Извлекаем рейтинг IMDb
        #     imdb_rating = response.css(
        #         'div[data-testid="hero-rating-bar__aggregate-rating__score"] span.sc-d541859f-1.imUuxf::text').get()
        #     if not imdb_rating:
        #         imdb_rating = response.css('span.ratingValue strong::text').get()
        #     elif not imdb_rating:
        #         imdb_rating = response.css('div[data-testid="hero-rating-bar__aggregate-rating__score"] span.sc-d541859f-1.imUuxf::text').get()
        #
        #     # Добавляем рейтинг к данным фильма
        #     movie["imdb_rating"] = imdb_rating.strip() if imdb_rating else "-"
        #
        #     # Возвращаем обновленные данные
        #     yield movie
