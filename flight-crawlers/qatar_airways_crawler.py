from base_crawler import BaseCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from datetime import datetime
import time
import csv
import os
from datetime import datetime
import re

class QatarAirwaysCrawler(BaseCrawler):
    """
    A subclass of BaseCrawler that specifically handles the scraping of flight data from the QatarAirways website.
    """

    airline_name = "QatarAirways"

    def __init__(self, departure_airport, destination_airport, date):
        """
        Initializes the QatarAirwaysCrawler with specific travel details.

        Parameters:
            departure_airport (str): The name of the departure airport.
            destination_airport (str): The name of the destination airport.
            date (str): The departure date in a string format.
        """
        self.departure_airport = departure_airport
        self.destination_airport = destination_airport
        self.date = date
        self.flight_data = []
        super().__init__(None, "QatarAirways")

    def run(self):
        """
        Executes the sequence of web scraping steps.
        """
        print(f"------------------ {self.airline_name}: {self.departure_airport} - {self.destination_airport} ------------------")
        self.url = self.construct_url()
        self.start_driver()
        self.open_url()
        self.accept_cookies()
        self.scrape_flight_data()
        self.save_results()
        self.stop_driver()

    def construct_url(self):
        """
        Constructs the URL for the flight search and logs the operation.

        Returns:
            str: The constructed URL with the flight search parameters.
        """
        try:
            base_url = (
                "https://www.qatarairways.com/app/booking/flight-selection?"
                "widget=QR&searchType=F&addTaxToFare=Y&upsellCallId=100&flexibleDate=off&bookingClass=E&"
                "tripType=O&selLang=de"
            )
            # Add parameters for departure airport, destination airport, and date
            params = {
                'fromStation': self.departure_airport,
                'toStation': self.destination_airport,
                'departing': self.date,
                'adults': '1',
                'children': '0',
                'infants': '0',
                'teenager': '0',
                'ofw': '0',
                'allowRedemption': 'N',
                'sort': 'price'
            }
            # Construct the URL with the given parameters
            url = (f"{base_url}&fromStation={params['fromStation']}&toStation={params['toStation']}&departing={params['departing']}"
                f"&adults={params['adults']}&children={params['children']}&infants={params['infants']}&teenager={params['teenager']}"
                f"&ofw={params['ofw']}&allowRedemption={params['allowRedemption']}&sort={params['sort']}")

            self.log_to_csv('INFO', 'Flight data URL constructed successfully')
            return url
        except Exception as e:
            self.log_to_csv('ERROR', 'Error constructing flight data URL')

    def open_url(self):
        """
        Opens the specified URL in the browser, waits for a specific element to ensure the page has loaded,
        and logs the process.

        Uses a retry mechanism with a maximum number of retries and a delay between retries to handle timeouts.
        """
        max_retries = 3  # Maximum number of retries for opening the URL
        retry_delay = 10  # Delay in seconds between retries

        try:
            self.driver.get(self.url)  # Attempt to open the URL

            for attempt in range(max_retries):
                try:
                    WebDriverWait(self.driver, 30).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="at-flight-search-result-1"]'))
                    )
                    self.log_to_csv('INFO', f"URL opened successfully: {self.url}")
                    return  # Exit the function if the element is found
                except TimeoutException:
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)  # Wait before retrying
                    else:
                        self.log_to_csv('ERROR', f"Timeout waiting for page to load after {max_retries} attempts: {self.url}")
        except Exception as e:
            self.log_to_csv('ERROR', "Error opening URL")

    def accept_cookies(self):
        """
        Attempts to close the cookie consent banner on the website if present and logs the action.
        """
        try:
            time.sleep(5) 
            self.driver.execute_script("window.scrollBy(0, 300);")  # Scroll down to trigger the cookie window
            time.sleep(2)  # Allow time for the scroll action and cookie banner to appear

            # Check for the presence of the cookie banner
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#cookie-id > div.cookie-btn.col-md-12 > div"))
            )

            try:
                # Wait for the accept button to be clickable and then click it
                accept_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#cookie-accept-all"))
                )
                accept_button.click()
                time.sleep(1)  # Pause after clicking to ensure processing
                self.log_to_csv('INFO', 'Accepted cookies successfully')
            except TimeoutException:
                self.log_to_csv('ERROR', 'Error accepting cookies')
        except TimeoutException:
            self.log_to_csv('INFO', 'Cookie window did not open, no accepting needed')


    def get_transit_duration(self):
        """
        Clicks on the flight result and extracts the transit duration from the details page, logs the process.

        The function waits for the flight result to be clickable, then extracts and formats the transit duration from the detail page.
        """
        try:
            time.sleep(5) 
            # Click on the flight result
            flight_detail_link_xpath = '//*[@id="at-flight-search-result-1"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[3]/div/div'
            
            details_button = WebDriverWait(self.driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, flight_detail_link_xpath))
            )
            details_button.click()
            self.log_to_csv('INFO', 'Flight details page clicked')

            # Wait for the details page to load and then extract the transit duration
            transit_duration_xpath = '/html/body/modal/div[2]/div/div[1]/div[2]/booking-smart-flight-details/qr-flight-details/div/div[3]/p'
            transit_duration_element = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, transit_duration_xpath))
            )

            transit_duration_text = transit_duration_element.text.strip()
            print("transit text: ", transit_duration_text)
            self.log_to_csv('INFO', 'Flight details page loaded successfully')

            # Extract the time (e.g., "2h 10m") from the text
            match = re.search(r'(\d+)h (\d+)m', transit_duration_text)
            if match:
                hours, minutes = match.groups()
                self.transit_duration = f"{int(hours):02}:{int(minutes):02}"
            else:
                self.transit_duration = "00:00"
            self.log_to_csv('INFO', 'Transit duration extracted')
        except TimeoutException:
            self.log_to_csv('ERROR', 'Timeout waiting for flight details to load')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error extracting transit duration')


    def scrape_flight_data(self):
        """
        Parses and collects flight data from the loaded page using Selenium WebDriver.

        Waits for the specific flight result element to be present, extracts various flight details like departure and arrival times,
        flight type, price, and airports. Logs the operation's success or any errors encountered.
        """
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="at-flight-search-result-1"]'))
            )
            flight_id = "at-flight-search-result-1"
            # XPaths for extracting flight details
            departure_time_xpath = f'//*[@id="{flight_id}"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[2]/div[1]/h3'
            arrival_time_xpath = f'//*[@id="{flight_id}"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[2]/div[3]/h3/span'
            flight_type_xpath = f'//*[@id="{flight_id}"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[2]/div[2]/p/div'
            price_xpath = f'//*[@id="{flight_id}"]/div/div/div[3]/div/div[1]/a/div[2]/span'
            departure_airport_xpath = f'//*[@id="{flight_id}"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[2]/div[1]/p/abbr'
            arrival_airport_xpath = f'//*[@id="{flight_id}"]/div/div/div[1]/booking-smart-flight-card/qr-flight-card/div/div[2]/div[3]/p/abbr'
            try:
                # Extract data from elements
                departure_time = self.driver.find_element(By.XPATH, departure_time_xpath).text.strip()
                arrival_time = self.driver.find_element(By.XPATH, arrival_time_xpath).text.strip()
                flight_type_duration = self.driver.find_element(By.XPATH, flight_type_xpath).text.strip()
                flight_type, travel_duration = flight_type_duration.split(', ')
                price_text = self.driver.find_element(By.XPATH, price_xpath).text.strip()
                departure_airport = self.driver.find_element(By.XPATH, departure_airport_xpath).text.strip()
                arrival_airport = self.driver.find_element(By.XPATH, arrival_airport_xpath).text.strip()

                # Formatting extracted data
                departure_time_formatted = datetime.strptime(departure_time, '%H:%M').strftime('%H:%M')
                arrival_time_formatted = datetime.strptime(arrival_time, '%H:%M').strftime('%H:%M')
                travel_duration_formatted = datetime.strptime(travel_duration, '%Hh %Mm').strftime('%H:%M')
                price = float(price_text.replace('€', '').replace(',', '').strip())

                # Check for nonstop flight
                if "Nonstop" in flight_type:
                    transit = False
                    transit_duration = "00:00"
                else:
                    transit = True
                    self.get_transit_duration()  # Extract transit time
                    transit_duration = self.transit_duration

                # Save the data in a list
                self.flight_data.append({
                    'airline_name': self.airline_name,
                    'crawling_date': datetime.now().strftime('%d-%m-%Y'),
                    'departure_airport': departure_airport,
                    'destination_airport': arrival_airport,
                    'date': datetime.strptime(self.date, '%Y-%m-%d').strftime('%d-%m-%Y'),
                    'travel_duration': travel_duration_formatted,
                    'departure_time': departure_time_formatted,
                    'arrival_time': arrival_time_formatted,
                    'transit': transit,
                    'transit_duration': transit_duration,
                    'price': price
                })

                self.log_to_csv('INFO', 'Flight data scraped successfully')
            except Exception as e:
                self.log_to_csv('ERROR', 'Error extracting flight data')

        except TimeoutException:
            self.log_to_csv('ERROR', 'Timeout waiting for flight results to load')