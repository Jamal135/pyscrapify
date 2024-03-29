''' Created: 10/09/2023 '''

# External Dependencies
from selenium.webdriver.remote.webdriver import WebDriver, WebElement
from bs4 import BeautifulSoup
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Union

# Internal Dependencies
from utilities.custom_exceptions import ScraperExceptions as SE

class BaseValidators(ABC):
    ''' Base class for scraper-specific validators. '''

    # Expected sibling Validators class values:
    url_pattern: str
    ''' url_pattern: Regex used to verify url for particular scraper. '''

    # Expected sibling Validators class functions:
    @abstractmethod
    def validate_data_block(self, block: List) -> None:
        ''' Purpose: Validates the given data block. '''

    # Sibling instance inherited BaseParsers class methods:
    def validate_url(self, url: str) -> None:
        if not re.compile(self.url_pattern).match(url):
            raise SE.InvalidConfigFile(f'JSON contains invalid URL format: {url}\n Given: {self.url_pattern}')

    # Enforce BaseValidators class attributes and abstract methods in sibling class:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        check_required_class_attributes(BaseValidators, cls)
        check_required_abstract_methods(BaseValidators, cls)

class BaseParsers(ABC):
    ''' Base class for scraper-specific Parsers. '''

    # Expected sibling Parsers class values:
    browser_lang: str
    ''' browser_lang: Language code for Chrome browser session. https://cloud.google.com/speech-to-text/docs/languages '''
    text_pattern: str
    ''' text_pattern: Regex used to spot data blocks inside texts list. '''
    text_idx: int
    ''' text_idx: Integer for expected_text index in data block. '''
    data_length: int
    ''' data_length: Integer for how many indexs long a data block is. '''

    # Expected sibling Parsers class functions:
    @abstractmethod
    def extract_total_count(self, driver: WebDriver) -> int:
        ''' Returns: Total number of data blocks to be extracted for current entry URL. '''
    @abstractmethod
    def extract_page_text(self, soup: BeautifulSoup) -> List[str]:
        ''' Returns: List of HTML element texts strings extracted from page soup. '''
    @abstractmethod
    def parse_data_block(self, block: List[str]) -> Dict[str, Union[int, str]]:
        ''' Returns: Data block parsed to dictionary of data to save. '''

    # Sibling instance inherited BaseParsers class methods:
    def extract_data_indices(self, texts: List[str]) -> List[int]:
        ''' Returns: List of indices of relevant data blocks in text list. '''
        return [i for i, x in enumerate(texts) if re.search(self.text_pattern, x)]
    def extract_data_bounds(self, idx: int) -> Dict[str, int]:
        ''' Returns: Dict of start and end indices for relevant data block in list. '''
        start_idx = idx - self.text_idx
        end_idx = idx + self.data_length - self.text_idx
        return {"start_idx": start_idx, "end_idx": end_idx}
    def extract_data_block(self, texts: List[str], data_bounds: Dict[str, int]) -> List[str]:
        ''' Returns: List of data blocks from full list of text. '''
        return texts[data_bounds['start_idx']:data_bounds['end_idx']]
    
    # Enforce BaseParsers class attributes and abstract methods in sibling class:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        check_required_class_attributes(BaseParsers, cls)
        check_required_abstract_methods(BaseParsers, cls)

class BaseNavigators(ABC):
    ''' Base class for scraper-specific Navigators. '''

    # Expected sibling Navigators class functions:
    @abstractmethod
    def check_next_page(self, driver: WebDriver) -> bool:
        ''' Returns: Boolean True or False if there is a next subpage. '''
    @abstractmethod
    def grab_next_page(self, driver: WebDriver) -> None:
        ''' Purpose: Navigates driver to the next subpage for scraping. '''
    @abstractmethod
    def wait_for_entry(self, driver: WebDriver) -> None:
        ''' Purpose: Waits for the entry URL webpage contents to load. '''
    @abstractmethod
    def wait_for_page(self, driver: WebDriver) -> None:
        ''' Purpose: Waits for the contents of the next subpage to update. '''
    
    # Enforce BaseNavigators class attributes and abstract methods in sibling class:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        check_required_class_attributes(BaseNavigators, cls)
        check_required_abstract_methods(BaseNavigators, cls)

def check_required_class_attributes(base_class, sub_class):
    ''' Purpose: Validates that sibling of given class contains all class level attributes. '''
    base_attrs = {k: v for k, v in base_class.__annotations__.items() if not callable(v) and not k.startswith('_')}
    for attr, _ in base_attrs.items():
        if getattr(sub_class, attr, None) is None:
            raise NotImplementedError(f'Class {sub_class.__name__} must define the {attr} class variable.')
        
def check_required_abstract_methods(base_class, sub_class):
    abstract_methods = base_class.__abstractmethods__
    for method in abstract_methods:
        if not callable(getattr(sub_class, method, None)):
            raise NotImplementedError(f'"{sub_class.__name__}" class needs to implement the "{method}" abstract method.')
