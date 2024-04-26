import datetime
from Scrapper import logger
import os
import re
import time

import dateutil.relativedelta
from slugify import slugify
from dateutil.parser import parse, ParserError
import requests
from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Archive import Archive
from selenium.webdriver.common.by import By

from Scrapper.locators import Locators


class LaTimes:
    def __init__(self, search, topics, month_range):
        if month_range == 0:
            month_range = 1
        self.browser_lib = Selenium()
        self.work_item_lib = WorkItems()
        self.excel_lib = Files()
        self.archive_lib = Archive()
        self.locator = Locators()
        self.search_phrase = search
        self.data = {
            'Title': [],
            'Description': [],
            'Date': [],
            'Image Path': [],
            'Price Status': [],
            'Phrase Count': []
        }
        self.topics = topics.split(',')
        self.month_range = datetime.datetime.now() - dateutil.relativedelta.relativedelta(months=month_range)

    def open_news_site(self, url):
        self.browser_lib.open_available_browser(url, maximized=True)

    def search_news_with_phrase(self):
        self.browser_lib.find_element(self.locator.search_icon).click()
        logger.info(f'Searching with phrase {self.search_phrase}')
        self.browser_lib.input_text_when_element_is_visible(self.locator.search_input, self.search_phrase)
        self.browser_lib.wait_and_click_button(self.locator.search_submit)

    def sort_by_latest(self):
        self.browser_lib.wait_until_element_is_visible(self.locator.sort_btn)
        self.browser_lib.select_from_list_by_value(self.locator.sort_btn, '1')

    def select_topic(self):
        for topic in self.topics:
            time.sleep(2)
            if self.browser_lib.does_page_contain_element(f'//span[text()="{topic}"]'):
                logger.info(f'Selecting topic {topic}')
                for see_all_button in self.browser_lib.find_elements(self.locator.see_all_btn):
                    self.browser_lib.scroll_element_into_view(see_all_button)
                    see_all_button.click()
                self.browser_lib.scroll_element_into_view(f'//span[text()="{topic}"]')
                self.browser_lib.click_element_when_visible(f'//span[text()="{topic}"]')

    def read_news(self):
        time.sleep(2)
        self.browser_lib.execute_javascript('window.scrollTo(0, document.body.scrollHeight);')
        self.browser_lib.wait_until_page_contains_element(self.locator.page_count)
        pages = self.browser_lib.find_element(self.locator.page_count).text.split('of')[-1].strip()
        for page_number in range(int(pages.replace(',', ''))):
            logger.info(f'reading news at page {page_number}')
            for news_element in self.browser_lib.find_elements(self.locator.news_list):
                date = news_element.find_element(By.XPATH, self.locator.date).text
                try:
                    datetime_obj = parse(date)
                    if datetime_obj < self.month_range:
                        logger.info(f'news at {datetime_obj} is older than {self.month_range} terminating')
                        return None
                except ParserError:
                    ...
                title = news_element.find_element(By.XPATH, self.locator.title).text
                desc = news_element.find_element(By.XPATH, self.locator.description).text
                image = news_element.find_element(By.XPATH, self.locator.image)
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
                self.data['Price Status'].append(str(contain_amount))
                self.data['Phrase Count'].append((title + desc).count(self.search_phrase))
                logger.info(f'got news {title}')
            self.browser_lib.scroll_element_into_view(self.locator.next_page)
            self.browser_lib.click_element_when_visible(self.locator.next_page)

    def save_news(self):
        self.excel_lib.create_workbook(path=f"{os.getcwd()}/output/news.xlsx", fmt="xlsx")
        self.excel_lib.append_rows_to_worksheet(self.data, header=True)
        self.excel_lib.save_workbook()
        self.archive_lib.archive_folder_with_zip(f"{os.getcwd()}/output", include="*.zip", archive_name=f"{os.getcwd()}/images")

    def start(self):
        try:
            logger.info('Process start')
            self.open_news_site("https://www.latimes.com/")
            logger.info('Searching phrase')
            self.search_news_with_phrase()
            logger.info('Applying topic filter')
            self.browser_lib.execute_javascript('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            if self.browser_lib.does_page_contain_element(self.locator.pop_up_module):
                self.browser_lib.wait_until_page_contains_element(self.locator.pop_up_module)
                pop_up = self.browser_lib.find_element(self.locator.pop_up_module)
                pop_close_button = self.browser_lib.driver.execute_script('return arguments[0].shadowRoot.querySelector("a")', pop_up)
                pop_close_button.click()
            self.select_topic()
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
