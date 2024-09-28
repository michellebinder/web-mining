import logging
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import random

class BaseCrawler:
    """
    A class used to represent a flight crawler for scraping flight information from airline websites.

    Attributes
    ----------
    url : str
        The URL of the airline website.
    airline_name : str
        The name of the airline.
    driver : WebDriver
        The Selenium WebDriver instance.
    log_dir : str
        The directory where log files will be stored.
    log_file : str
        The path to the log file for the specific airline.
    logger : Logger
        The logger instance for logging messages and errors.
    """
    def __init__(self, url, airline_name):
        """
        Constructs all the necessary attributes for the BaseCrawler object.

        Parameters
        ----------
        url : str
            The URL of the airline website.
        airline_name : str
            The name of the airline.
        """
        self.url = url
        self.airline_name = airline_name
        self.driver = None
        self.log_dir = 'logs'
        self.log_file = os.path.join(self.log_dir, f'logging_{self.airline_name}.csv')
        self.setup_logger()

    def setup_logger(self):
        """
        Sets up the logger for logging messages and errors.
        """
        if not os.path.exists(self.log_dir):  
            os.makedirs(self.log_dir)  
        
        if not os.path.exists(self.log_file):  
            with open(self.log_file, 'w', newline='') as csvfile: 
                fieldnames = ['date', 'time', 'level', 'message', 'error']  
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
                writer.writeheader()  
        
        self.logger = logging.getLogger(self.airline_name)  
        self.logger.setLevel(logging.INFO)  

        if not self.logger.handlers:  
            console_handler = logging.StreamHandler()  
            console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')  
            console_handler.setFormatter(console_formatter)  
            self.logger.addHandler(console_handler) 

    def log_to_csv(self, level, message, error=None):
        """
        Logs messages and errors to a CSV file and the console.

        Parameters
        ----------
        level : str
            The log level (e.g., 'INFO', 'ERROR').
        message : str
            The log message.
        error : str, optional
            The error message, if any (default is None).
        """
        with open(self.log_file, 'a', newline='') as csvfile:  
            fieldnames = ['date', 'level', 'message', 'error'] 
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)  
            now = datetime.now()  
            date_str = now.strftime('%Y-%m-%d')  
            writer.writerow({
                'date': date_str,
                'level': level,
                'message': message,
                'error': error
            }) 
        self.logger.log(getattr(logging, level), f"{message}, {error if error else ''}") 

    def start_driver(self):
        """
        Starts the Selenium WebDriver.
        """
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
        self.log_to_csv('INFO', f"Selenium WebDriver for {self.airline_name} started ({self.departure_airport} - {self.destination_airport})")

    def start_driver_klm(self):
        """
        Starts the Selenium WebDriver for KLM, because specific configurations are needed to crawl that website.
        """
        service = Service()
        options = webdriver.ChromeOptions()
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                window.navigator.chrome = {
                    runtime: {}
                };
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            """
        })
        print(f"------------------ started crawling for airline {self.airline_name} ------------------")
        self.log_to_csv('INFO', f"Selenium WebDriver for {self.airline_name} started.")

    def stop_driver(self):
        """
        Stops the Selenium WebDriver.
        """
        if self.driver:
            self.driver.quit()
            self.log_to_csv('INFO', f"Selenium WebDriver for {self.airline_name} stopped")
            
    def open_url(self):
        """
        Opens the specified URL in the browser.
        """
        try:
            self.driver.get(self.url)
            self.log_to_csv('INFO', f"URL opened: {self.url}")
        except Exception:
            self.log_to_csv('ERROR', "Error opening URL")

    def save_results(self):
        """
        Saves the scraped data to a CSV file.
        """
        results_file = f'results/results_{self.airline_name}.csv'
        fieldnames = [
            'airline_name', 'crawling_date', 'departure_airport', 'destination_airport', 
            'date', 'travel_duration', 'departure_time', 'arrival_time', 
            'transit', 'transit_duration', 'price'
        ]

        if not os.path.exists('results'):
            os.makedirs('results')

        file_exists = os.path.isfile(results_file)
        mode = 'a' if file_exists else 'w'  

        with open(results_file, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()  
            writer.writerows(self.flight_data)

        self.log_to_csv('INFO', f'Results saved to {results_file}')