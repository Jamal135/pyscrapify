# PyScrapify - Basic Web Scraper Framework

***
# About:

> Note: It is recommended you understand the disclaimer contained within this readme.md file prior to any use of this web scraping framework.

**PyScrapify** is a robust web scraping framework developed in Python `3.10.2` built ontop of [Selenium](https://github.com/SeleniumHQ/selenium) and [BeautifulSoup](https://github.com/wention/BeautifulSoup4). The framework is designed to streamline the creation of new web scrapers by implementing scraper control logic out of the box, reducing the redundant boilerplate code often associated with building Python-based web scrapers from scratch.

Scrapers have three key elements: Validators, Parsers, and Navigators. The data Parsers class forms the core logic of PyScrapify and is built to extract data based on four key assumptions: 

1. We can enter a given website at configured entry URLs. 
2. We can create a function for converting each entry URL and each of its subpages source HTML soup into a list of strings that includes desired data. 
3. We can regex match a string that when present indicates the presence of a desired data block, which is a subset of the list of strings.
4. We can expect the data blocks we are extracting to be of a common format and length.

The core execution flow is initiated through `scraper_controller.py`, triggered via the `launcher.py` command-line interface.

***
# Usage:

This usage section covers installation, settings, configuration of existing scrapers, and implementing new scrapers.

## Installation:

Currently this repository uses a `requirements.txt` for dependency management. It is recommended to create a virtual environment, then run `pip install -r requirements.txt` inside that virtual environment. You also need Chrome installed on your computer.

## Configuration:

On first usage of the scraper via `launcher.py` a `settings.yml` file will be created in the repository root directory with a default configuration loaded. Modifying the values in this YML file will override the default configurations defined in the utilities [settings.py](https://github.com/Jamal135/pyscrapify/blob/main/utilities/settings.py). See key configuration settings below:

>**Settings**:
>
>* `PICK_OUTPUT_NAME`: Boolean True or False, if True name is generated, if False `launcher.py` will prompt you in CLI to enter a name.
>* `GENERATED_OUTPUT_NAME_BASE`: String name for the scraper result outputs. A number will be added to the end to keep results unique.
>* `RATE_LIMIT_DELAY`: Integer value for a sleep delay in seconds to minimise scraping activity impacts. See disclaimer before changing.
>* `SELENIUM_LOGGING`: Boolean True or False, if True Selenium specific logs will be printed to CLI as they occur. Useful for some troubleshooting.
>* `SELENIUM_HEADER`: Boolean True or False, if True Selenium will run with a header (browser you can see). Very useful for troubleshooting and scraper development.
>* `DATA_STRICT`: Boolean True or False, if False the `scraper_controller.py` will allow some unexpected data and try work with it, whilst logging a warning. This risks the integrity of your data but may fix some issues.

## Using an Existing Scraper:

To use an existing scraper, follow these steps:

1. **Create a Configuration File**: Go to the `scrape_configs` directory and create a new JSON file. This file must contain:

    - The `scraper` key with the name of the scraper you want to use (check the `scrapers` directory for available options, BaseScraper is the parent class).
    - The `entries` key with an object of names and entry URLs for data extraction.

    Example configuration:
    ```json
    {
        "scraper": "Seek",
        "entries": {
            "Target Australia": "https://www.seek.com.au/companies/target-432304/reviews"
        }
    }
    ```

2. **Run the Scraper**: Execute `launcher.py` and select the configuration file you created when prompted in the command line interface. The scraper will process each entry URL defined in your configuration file.

## Creating a New Scraper:

Creating a new scraper is a more involved process, requiring coding. To first give some context to what you are doing when you implement a new scraper, you are defining siblings for [BaseScraper.py](https://github.com/Jamal135/pyscrapify/blob/main/scrapers/BaseScraper.py) classes that specify expected values and implement expected methods:

>**Validators**:
>
>Implementing the scraper specific Validators value and method below is recommended, though is not required. At the risk of bad data, bad URLs, and unexpected errors, you can pass a `url_pattern` for any string and define `validate_data_block` to just pass.
>
>* `url_pattern`: Regex pattern to match to valid entry URLs. This pattern is used to verify all entry URLs in the configuration JSON.
>
>* `validate_data_block`: Method that validates that an extracted data block is as expected, you should raise a `SE.UnexpectedData('message')` error if validation fails.

>**Parsers**:
>
>Implementing the scraper specific Parsers values and methods is required.
>
>* `browser_lang`: Language code string to be used by Selenium Chrome Driver browser session. See available [language codes](https://cloud.google.com/speech-to-text/docs/languages).
>* `text_pattern`: Regex pattern to match to strings in a list of strings extracted from page source HTML soup. Should match all locations that have a block of relevant data.
>* `text_idx`: Integer value for howmany indexs into a data block the text_pattern string is expected to be.
>* `data_length`: Integer value for howmany indexs long a data block of relevant strings is expected to be. 
>
>* `extract_total_count`: Method for returning the number of data blocks expected to be extracted from a given entry URL and associated subpages. Value is used for validation.
>* `extract_page_text`: Method for converting a entry URL page or subpage source HTML soup into a list of strings. Ensure this list contains all desired page data blocks for further processing.
>* `parse_data_block`: Method that takes in a list of strings for one data block and parses the data to a dictionary of integers or strings where dictionary keys are the desired CSV data column names. 

>**Navigators**:
>
>Implementing the scraper specific Navigators methods is required. It is recommended to implement dynamic waits for the wait methods though you can also use static sleep statement waits. If not scraping multiple subpages, `check_next_page` can always return False, `grab_next_page` and `wait_for_page` can always pass, though you still require `wait_for_entry`.
>
>* `check_next_page`: Method for determining if the current entry page has a next subpage that needs to be navigated to.
>* `grab_next_page`: Method for interacting with the current Selenium browser session to navigate to the next subpage of a given entry page.
>* `wait_for_entry`: Method for dynamicly or staticly waiting for a given entry URL to finish loading desired data.
>* `wait_for_page`: Method for dynamically or staticly waiting for a given entry URL subpage to finish loading desired data.

To create a new scraper, follow these steps:

1. **Create New Scraper**: Go to the `scrapers` directory and create a new Python file, populate the file with a base template. You may also want to create a test JSON configuration (where the new scraper python filename is the scraper name) and enable `SELENIUM_HEADER` in the `settings.yml` to assist in further development. 

    Example template:

    ```python
    # External Dependencies
    from selenium.webdriver.remote.webdriver import WebDriver
    from bs4 import BeautifulSoup
    from typing import List, Dict, Union

    # Internal Dependencies
    from utilities.custom_exceptions import ScraperExceptions as SE
    from scrapers.BaseScraper import BaseValidators, BaseParsers, BaseNavigators

    class Validators(BaseValidators):

        url_pattern = r''

        def validate_data_block(self, block: List) -> None:
            raise SE.UnexpectedData('message') # If validation fails

    class Parsers(BaseParsers):

        browser_lang = 'en-AU'
        text_pattern = r''
        text_idx = 0
        data_length = 0

        def extract_total_count(self, driver: WebDriver) -> int:
            pass
        
        def extract_page_text(self, soup: BeautifulSoup) -> List[str]:
            pass
        
        def parse_data_block(self, block: List[str]) -> Dict[str, Union[int, str]]:
            pass

    class Navigators(BaseNavigators):
        
        def check_next_page(self, driver: WebDriver) -> bool:
            pass
        
        def grab_next_page(self, driver: WebDriver) -> None:
            pass
            
        def wait_for_entry(self, driver: WebDriver) -> None:
            pass

        def wait_for_page(self, driver: WebDriver) -> None:
            pass
    ```

2. **Develop Scraper Functionality**: Implement all methods and define all values for each of the Validators, Parsers, and Navigators classes. It is recommended to regularly test the scraper as you make progress, this can also assist in providing order to what you implement.

Access an example implementation here: [Seek.py](https://github.com/Jamal135/pyscrapify/blob/main/scrapers/Seek.py).

***

# Contribution:

I welcome new ideas and contributions. If you have ideas or wish to implement features, please open an issue.

# Disclaimer:

This tool has been developed solely for educational, research, and public interest purposes. Users are independently responsible for:

1. Complying with the Terms of Service (ToS) of the target website with respect to its stipulations and intentions, note enforceability may vary. 
2. Adhering to applicable copyright and privacy legislation when scraping, storing, using, or publishing any data from the target website.
3. Ensuring scraping activities do not disrupt the normal operations of the target website or otherwise breach anti-hacking or computer fraud legislation.
4. Conducting scraping activities in a way that does not exploit unauthorised access or disregard the target website robots.txt guidelines.

By using this tool, users agree to act ethically and within legal boundaries. They acknowledge that the creators and maintainers of this repository neither endorse nor encourage any actions that could breach laws, regulations, or binding website terms. We disclaim liability for any misuse of this tool or any consequences thereof. The field of web scraping intersects with complex and evolving legal domains, including privacy, copyright, computer fraud, internet law, and contract law. Users are advised to remain informed and consult with legal professionals before engaging in web scraping activities.

Website providers with concerns about the scraping functionality contained in this repository are encouraged to open an issue so we can work to resolve any concerns.

***
# Acknowledgements:

This project was originally just an employee employer review scraper for Indeed and Seek. At that time, this project was inspired by the work of [Tim Sauchuk](https://github.com/tim-sauchuk) on a now broken [Indeed.com scrape tool](https://github.com/tim-sauchuk/Indeed-Company-Review-Scraper).

Additionally, [McJeffr](https://github.com/McJeffr) provided valuable feedback that helped in guiding this project originally.

***
# Future:

In future I will continue to work on resolving bugs and improving the functionality of the core framework. Additionally, where appropriate, I will work to repair scrapers added to the official repository. Feel free to suggest ideas, here are some current goals for future versions:

>Roadmap to `v2.0`
>
>* Ensure Linux and Windows compatibility
>* Move to more robust dependency manager
  
>Roadmap to `v2.1`
>
>* Explore making pyscrapify a pip package
>* Explore approaches to simplify the creation of new scrapers

***
# License:

Copyright (c) [@Jamal135](https://github.com/Jamal135)

MIT License
