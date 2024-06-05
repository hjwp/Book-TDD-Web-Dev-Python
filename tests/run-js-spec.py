#!python
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By


def run(path: Path):
    assert path.exists()

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)

    try:
        browser.get(f"file:///{path}")
        time.sleep(0.2)

        for sel in [
            ".jasmine-overall-result" ".jasmine-duration",
            ".jasmine-description",
            ".jasmine-summary",
            ".jasmine-result-message",
            ".jasmine-stack-trace",
        ]:
            for el in browser.find_elements(By.CSS_SELECTOR, sel):
                print(
                    re.sub(
                        r"@file://(.+)/superlists/src/",
                        ".../goat-book/src/",
                        el.text,
                    )
                )
    finally:
        browser.quit()


if __name__ == "__main__":
    _, fn, *__ = sys.argv
    if fn.endswith("Spec.js"):
        fn = fn.replace("Spec.js", "SpecRunner.html")
    run(Path(fn).resolve())
