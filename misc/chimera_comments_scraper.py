from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import re

URLS = [
    'http://chimera.labs.oreilly.com/books/1234000000754/pr01.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/pr02.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch01.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch02.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch03.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch04.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch05.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch06.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch07.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch08.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch09.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch10.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch11.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch12.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch13.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch14.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch15.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch16.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch17.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch18.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch19.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch20.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch21.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch22.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/pr03.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/apa.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/apb.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/apc.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/apd.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ape.html',
]

METADATA_PARSER = re.compile(r'Comment by (.+) (\d+) (.+ ago)')
browser = webdriver.Firefox()
wait = WebDriverWait(browser, 3)
try:
    for url in URLS:
        page = url.partition('1234000000754/')[2]
        browser.get(url)

        browser.find_element_by_css_selector('#comments-link a').click()
        try:
            wait.until(expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, 'comment')
            ))
        except TimeoutException:
            print("No comments on page %s" % (url,))

        elements = browser.find_elements_by_css_selector('.comment')
        for element in elements:
            metadata = element.find_element_by_css_selector('.comment-body-top').text.strip()
            # print(repr(metadata))
            parsed_metadata = METADATA_PARSER.search(metadata).groups()
            # print(parsed_metadata)
            by = parsed_metadata[0]
            date = parsed_metadata[1] + parsed_metadata[2]
            # if 'months' not in date and 'year' not in date:
            if 'year' not in date:
                comment = element.find_element_by_css_selector('.comment-body-bottom').text
                print('%s\t%s\t%s\t%s' % (page, by, date, comment))

finally:
    browser.quit()

