#!/usr/bin/env python3
"""Run a qunit test with selenium/phantomjs

Usage:
  my_runner.py <path_to_tests.html>

Options:
  -h --help                                 Show this screen.

"""
from docopt import docopt
from selenium import webdriver
import os

def main(path):
    browser = webdriver.PhantomJS()
    try:
        browser.get('file:///' + path)
        body = browser.find_element_by_tag_name('body')
        #print(browser.page_source)
        #print(body.text)
        print()
        overall_result = browser.find_element_by_id('qunit-testresult')
        headline = overall_result.text.split('\n')[1]
        print(headline)
        test_lis = browser.find_elements_by_css_selector('#qunit-tests li')
        tests = [
            li for li in test_lis
            if 'qunit-test-output' in li.get_attribute('id')
        ]
        for ix, test in enumerate(tests):
            result_text = test.text.split('\n')[0]
            result_text = result_text.replace('Rerun', '')
            print('{}. {}'.format(ix + 1, result_text))

    finally:
        browser.quit()


if __name__ == '__main__':
    arguments = docopt(__doc__)
    path = os.path.abspath(arguments['<path_to_tests.html>'])
    main(path)

