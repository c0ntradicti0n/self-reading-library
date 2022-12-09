import os
if __name__== "__main__":
    import sys
    sys.path.append(os.getcwd())

from regex import regex

from config import config
from helpers.cache_tools import configurable_cache

import logging

from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@converter("arxiv.org", "tex")
class Scraper(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cwd = os.getcwd() + "/"
        self.save_dir = config.tex_data
        if not os.path.isdir(self.save_dir):
            os.system(f"mkdir {config.tex_data}")

    http_regex = r"(https?:\/\/(?:www\.|(?!www))?[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
    file_regex = "([-a-z%A-Z0-9./]+)+\.pdf"

    @configurable_cache(
        config.cache + os.path.basename(__file__),
        from_path_glob=config.hidden_folder + "/pdfs/**/*.pdf",
    )
    def __call__(self, i_url):
        for id, meta in i_url:
            if "url" in self.flags and self.flags["url"]:
                url = self.flags["url"]
            else:
                url = id

            if url and url.startswith("http") and regex.match(self.http_regex, url):
                path = id
                if os.path.exists(path):
                    yield path, meta

                path = path.replace("(", "")
                path = path.replace(")", "")
                meta["url"] = self.flags["url"]

                if not os.path.exists(path):
                    self.scrape(url, path)
                yield id, meta
            elif os.path.exists(id) and regex.match(self.file_regex, id) is not None:
                yield id, meta
            else:
                logging.error(f"{id} is not a valid url/path")

    def scrape(self, url, path):

        import os
        import time

        import selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By

        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        time.sleep(3)

        elements = driver.find_elements(By.CSS_SELECTOR, "svg")
        time.sleep(3)

        for element in elements:
            try:
                driver.execute_script(
                    f"""
                var img = document.createElement('img');
                img.width = {element.size['width']}
                img.src =\"data:image/png;base64, {element.screenshot_as_base64}\"
                arguments[0].outerHTML = img.outerHTML
                """,
                    element,
                )
            except selenium.common.exceptions.WebDriverException:
                driver.execute_script(
                    f"""
                        arguments[0].remove()
                        """,
                    element,
                )
        bad_images = driver.find_elements("xpath", "//*[starts-with(@src,'data')]")
        for element in bad_images:
            driver.execute_script(
                f"""
                            arguments[0].remove()
                            """,
                element,
            )
        try:
            button = driver.find_element("xpath", "//*[text()='Accept']")
            button.click()
        except:
            self.logger.warning("Found no cookie banner, but cool")

        source = driver.page_source.encode("utf-8").decode()
        if (
            not "Occasionally, you may see this page while the site ensures that the connection is secure."
            in source
        ):
            with open(f"./{path}.htm", "w") as f:
                f.write(source)
            os.system(f"pandoc {path}.htm  --pdf-engine xelatex --to pdf -o {path}")
        else:
            os.system(f"pandoc {url} --pdf-engine xelatex --to pdf -o {path}")

import unittest
class T(unittest.TestCase):
    def case(self, url, pdf):
        Scraper.scrape(url,pdf)
        self.assertTrue(os.path.exists(pdf))

    def test_db_com(self):
        self.case(
            "https://www.differencebetween.com/what-is-the-difference-between-total-solids-and-total-suspended-solids/",
            "differencebetween.com.pdf")

    def test_db_net(self):
        self.case(
            "http://www.differencebetween.net/miscellaneous/difference-between-ambivalent-sexism-and-social-dominance/",
            "differencebetween.net.pdf")



if __name__ == "__main__":
    unittest.main()


