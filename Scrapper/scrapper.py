import logging
import os
import re
import time
from slugify import slugify
import requests
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
from selenium.webdriver.common.by import By

from Scrapper.locators import Locators


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


class LaTimes:
    def __init__(self, search):
        self.browser_lib = Selenium()
        self.work_item_lib = WorkItems()
        self.excel_lib = Files()
        self.locator = Locators()
        self.search_phrase = search
        self.data = {
            'Date': [],
            'Title': [],
            'Description': [],
            'Image Path': [],
            'Price Status': [],
            'Phrase Count': []
        }

    def open_news_site(self, url):
        self.browser_lib.open_available_browser(url, maximized=True)

    def search_news_with_phrase(self):
        self.browser_lib.find_element(self.locator.search_icon).click()
        self.browser_lib.input_text_when_element_is_visible(self.locator.search_input, self.search_phrase)
        self.browser_lib.wait_and_click_button(self.locator.search_submit)

    def sort_by_latest(self):
        self.browser_lib.select_from_list_by_value(self.locator.sort_btn, '1')

    def select_topic(self, topic):
        for see_all_button in self.browser_lib.find_elements('//span[text()="See All"]'):
            self.browser_lib.scroll_element_into_view(see_all_button)
            see_all_button.click()
        self.browser_lib.scroll_element_into_view(f'//span[text()="{topic}"]')
        self.browser_lib.click_element_when_visible(f'//span[text()="{topic}"]')

    def read_news(self):
        time.sleep(2)
        self.browser_lib.execute_javascript('window.scrollTo(0, document.body.scrollHeight);')
        pages = self.browser_lib.find_element('//div[@class="search-results-module-page-counts"]').text.split('of')[-1].strip()
        for page_number in range(int(pages.replace(',', ''))):
            logger.info(f'reading news at page {page_number}')
            for news_element in self.browser_lib.find_elements('//ul[@class="search-results-module-results-menu"]/li'):
                date = news_element.find_element(By.XPATH, './/p[@class="promo-timestamp"]').text
                title = news_element.find_element(By.XPATH, './/h3[@class="promo-title"]').text
                desc = news_element.find_element(By.XPATH, './/p[@class="promo-description"]').text
                image = news_element.find_element(By.XPATH, './/img')
                image_url = image.get_attribute('src')
                response = requests.get(image_url)
                image_path = os.path.join(f"{os.getcwd()}/output/{slugify(title, separator='_')}.png")
                with open(image_path, 'wb') as file:
                    file.write(response.content)
                contain_amount = False
                for pattern in [r'\$\d+(\.\d+)?', r'\d+(\.\d+)? dollars', r'\d+(\.\d+)? USD']:
                    if re.search(pattern, title + desc):
                        contain_amount = True
                        break
                self.data['Date'].append(date)
                self.data['Title'].append(title)
                self.data['Description'].append(desc)
                self.data['Image Path'].append(image_path)
                self.data['Price Status'].append(contain_amount)
                self.data['Phrase Count'].append((title + desc).count(self.search_phrase))
            self.browser_lib.click_element_when_visible('//div[@class="search-results-module-next-page"]')

    def save_news(self):
        self.excel_lib.create_workbook(path=f"{os.getcwd()}/output/news.xlsx", fmt="xlsx")
        self.excel_lib.append_rows_to_worksheet(self.data, header=True)
        self.excel_lib.save_workbook()

    def start(self):
        try:
            logger.info('Process start')
            self.open_news_site("https://www.latimes.com/")
            logger.info('Searching phrase')
            self.search_news_with_phrase()
            logger.info('Applying topic filter')
            topics = ['Lifestyle']
            self.browser_lib.execute_javascript('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            if self.browser_lib.does_page_contain_element('//modality-custom-element'):
                self.browser_lib.wait_until_page_contains_element('//modality-custom-element')
                pop_up = self.browser_lib.find_element('//modality-custom-element')
                pop_close_button = self.browser_lib.driver.execute_script('return arguments[0].shadowRoot.querySelector("a")', pop_up)
                pop_close_button.click()
            for topic in topics:
                self.select_topic(topic=topic)
            logger.info('Sorting results')
            self.sort_by_latest()
            logger.info('scrapping news')
            self.read_news()
            logger.info('Saving news')
            self.save_news()
            logger.info('Process finish')
        except Exception as e:
            self.browser_lib.capture_page_screenshot(f'{os.getcwd()}/output/error.png')
            raise e
