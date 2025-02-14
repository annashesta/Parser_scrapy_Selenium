# python Selenium/Selenium_rating_movies.py

import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Настройка Selenium
def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    return webdriver.Chrome()

# Функция для получения рейтинга IMDb
def get_imdb_rating(driver, url):
    driver.get(url)
    time.sleep(2)  # Даем странице время для загрузки
    try:
        # Попытка извлечь рейтинг с новым селектором
        imdb_rating = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="hero-rating-bar__aggregate-rating__score"] span.sc-d541859f-1.imUuxf').text
    except:
        try:
            # Попытка извлечь рейтинг с альтернативным селектором
            imdb_rating = driver.find_element(By.CSS_SELECTOR, 'span.ratingValue strong').text
        except:
            imdb_rating = "Рейтинг не найден"
    return imdb_rating

# Функция для обработки одной строки
def process_row(row):
    imdb_id = row['imdb_id']
    if imdb_id and imdb_id != "-":  # Проверяем, есть ли IMDb ID
        driver = create_driver()  # Создаем отдельный драйвер для каждого потока
        imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
        print(f"Parsing IMDb URL: {imdb_url}")
        imdb_rating = get_imdb_rating(driver, imdb_url)
        row['imdb_rating'] = imdb_rating  # Обновляем рейтинг
        print(row)
        driver.quit()  # Закрываем драйвер после использования
    else:
        row['imdb_rating'] = "-"  # Если IMDb ID отсутствует
        print(row)
    return row

# Чтение данных из movies.csv
input_file = '../movies.csv'
output_file = '../rating_movies_selenium.csv'

# Открываем файл для чтения и создаем новый файл для записи
with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames  # Заголовки столбцов
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()  # Записываем заголовки в новый файл
    outfile.flush()  # Сбрасываем буфер, чтобы заголовки сразу записались

    # Создаем пул потоков
    with ThreadPoolExecutor(max_workers=5) as executor:  # Максимум 5 потоков
        futures = []
        for row in reader:
            # Запускаем обработку строки в отдельном потоке
            future = executor.submit(process_row, row)
            futures.append(future)

        # Обрабатываем результаты по мере их завершения
        for future in as_completed(futures):
            try:
                updated_row = future.result()  # Получаем результат
                writer.writerow(updated_row)  # Записываем обновленную строку
                outfile.flush()  # Сбрасываем буфер, чтобы данные сразу записывались в файл
            except Exception as e:
                print(f"Ошибка при обработке строки: {e}")



######
# Так как многопоточность я ввела в качестве эксперимента,
# закомментировала так же вариант без многопоточности,
# он парсит медленее, но компьютер при этом не тормозит.
# Это был мой первый работающий вариант:
######

# import csv
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# import time
#
# # Настройка Selenium
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Запуск в фоновом режиме
# chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--no-sandbox")
# driver = webdriver.Chrome()
#
# # Функция для получения рейтинга IMDb
# def get_imdb_rating(url):
#     driver.get(url)
#     time.sleep(2)  # Даем странице время для загрузки
#     try:
#         # Попытка извлечь рейтинг с новым селектором
#         imdb_rating = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="hero-rating-bar__aggregate-rating__score"] span.sc-d541859f-1.imUuxf').text
#     except:
#         try:
#             # Попытка извлечь рейтинг с альтернативным селектором
#             imdb_rating = driver.find_element(By.CSS_SELECTOR, 'span.ratingValue strong').text
#         except:
#             imdb_rating = "Рейтинг не найден"
#     return imdb_rating
#
# # Чтение данных из movies.csv
# input_file = '../../movies.csv' # этот файл мы получили парсером wiki_movie_parser
# output_file = '../../rating_movies_selenium.csv'
#
# # Открываем файл для чтения и создаем новый файл для записи
# with open(input_file, mode='r', encoding='utf-8') as infile, open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
#     reader = csv.DictReader(infile)
#     fieldnames = reader.fieldnames  # Заголовки столбцов
#     writer = csv.DictWriter(outfile, fieldnames=fieldnames)
#     writer.writeheader()  # Записываем заголовки в новый файл
#     outfile.flush()  # Сбрасываем буфер, чтобы заголовки сразу записались
#
#     # Обрабатываем каждую строку
#     for row in reader:
#         imdb_id = row['imdb_id']
#         if imdb_id and imdb_id != "-":  # Проверяем, есть ли IMDb ID
#             imdb_url = f"https://www.imdb.com/title/{imdb_id}/"
#             print(f"Parsing IMDb URL: {imdb_url}")
#             imdb_rating = get_imdb_rating(imdb_url)
#             row['imdb_rating'] = imdb_rating  # Обновляем рейтинг
#             print(row)
#
#         else:
#             row['imdb_rating'] = "-"  # Если IMDb ID отсутствует
#             print(row)
#
#         # Записываем обновленную строку в новый файл
#         writer.writerow(row)
#         outfile.flush()  # Сбрасываем буфер, чтобы данные сразу записывались в файл
#
# # Закрытие драйвера Selenium
# driver.quit()