from selenium import webdriver
browser = webdriver.Firefox()
URLS = [
    'http://chimera.labs.oreilly.com/books/1234000000754/pr01.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch01.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch02.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch03.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch04.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch05.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch06.html',
    'http://chimera.labs.oreilly.com/books/1234000000754/ch07.html',
]


try:
    for url in URLS:
        page = url.partition('1234000000754/')[2]
        browser.get(url)
        elements = browser.find_elements_by_css_selector('.comment')
        for element in elements:
            metadata = element.find_element_by_css_selector('.comment-body-top').text
            by = metadata.split()[2]
            date = ' '.join(metadata.split()[3:])

            comment = element.find_element_by_css_selector('.comment-body-bottom').text
            print page, '\t', by, '\t', date, '\t', comment

finally:
    browser.quit()

