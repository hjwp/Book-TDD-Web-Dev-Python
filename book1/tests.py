from selenium import webdriver
browser = webdriver.Firefox()
browser.get('http://localhost:8001')
assert 'Django' in browser.title
browser.quit()
