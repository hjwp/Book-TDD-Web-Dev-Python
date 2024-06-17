#!python
import re
import sys
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


def sub_book_path(text: str) -> str:
    return re.sub(
        r"@file://(.+)/superlists/src/",
        ".../goat-book/src/",
        text,
    )


def run(path: Path):
    assert path.exists()

    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    browser = webdriver.Firefox(options=options)
    failed = False

    def _el_text(sel, node: webdriver.Remote | WebElement = browser):
        return "\n".join(el.text for el in node.find_elements(By.CSS_SELECTOR, sel))

    try:
        browser.get(f"file:///{path}?seed=12345")
        time.sleep(0.2)

        print(
            f"{_el_text('.jasmine-overall-result')}\t\t{_el_text('.jasmine-duration')}"
        )

        print(_el_text(".jasmine-bar.jasmine-errored"))

        print(_el_text(".jasmine-menu.jasmine-failure-list"))
        for failures_el in browser.find_elements(By.CSS_SELECTOR, ".jasmine-failures"):
            for spec_failure in failures_el.find_elements(
                By.CSS_SELECTOR, ".jasmine-spec-detail.jasmine-failed"
            ):
                failed = True
                print()
                print(_el_text(".jasmine-description", spec_failure))
                print(_el_text(".jasmine-messages", spec_failure))

        for success_el in browser.find_elements(By.CSS_SELECTOR, ".jasmine-summary"):
            for suite_el in success_el.find_elements(By.CSS_SELECTOR, ".jasmine-suite"):
                if suite_el.is_displayed():
                    print(_el_text("li.jasmine-suite-detail", suite_el))
                    for spec_el in suite_el.find_elements(
                        By.CSS_SELECTOR, "ul.jasmine-specs li.jasmine-passed"
                    ):
                        print("  * " + spec_el.text)

    finally:
        browser.quit()
    return failed


if __name__ == "__main__":
    _, fn, *__ = sys.argv
    if fn.endswith("Spec.js"):
        fn = fn.replace("Spec.js", "SpecRunner.html")
    failed = run(Path(fn).resolve())
    sys.exit(1 if failed is True else 0)
