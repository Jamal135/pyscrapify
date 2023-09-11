''' Created: 12/09/2023 '''

# External Dependencies
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.remote.webdriver import WebDriver

# Internal Dependencies
from logger import Log

class BrowserManager:
    def __init__(self, header: bool = False, logging: bool = False):
        self.header = header
        self.logging = logging
    def create_browser(self) -> WebDriver:
        ''' Returns: Created Selenium Chrome browser session. '''
        options = webdriver.ChromeOptions()
        if not self.header:
            Log.info('Running Selenium driver without header...')
            options.add_argument('--headless')
        if not self.logging:
            Log.info('Disabled Selenium driver logging...')
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), 
            options=options)
        return driver
    def __enter__(self):
        self.driver = self.create_browser()
        return self.driver
    def __exit__(self, *_):
        Log.info('Ending Selenium driver...')
        self.driver.quit()