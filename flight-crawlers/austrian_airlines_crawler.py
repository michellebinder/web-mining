from base_crawler import BaseCrawler
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC
import time
import csv
import os
import locale
from datetime import datetime, timedelta
import re

class AustrianAirlinesCrawler(BaseCrawler):
    """
    A subclass of BaseCrawler that specifically handles the scraping of flight data from the Austrian Airlines website.
    """

    airline_name = "AustrianAirlines"

    def __init__(self, departure_airport, destination_airport):
        """
        Initializes the AustrianAirlinesCrawler with specific travel details.

        Parameters:
            departure_airport (str): The name of the departure airport.
            destination_airport (str): The name of the destination airport.
        """
        url = "https://www.austrian.com"
        self.departure_airport = departure_airport
        self.destination_airport = destination_airport
        self.flight_data = []
        super().__init__(url, "AustrianAirlines")

    def run(self):
        """
        Executes the sequence of web scraping steps.
        """
        print(f"------------------ {self.airline_name}: {self.departure_airport} - {self.destination_airport} ------------------")
        self.start_driver()
        self.open_url()
        self.accept_cookies()
        self.enter_departure_airport(self.departure_airport)
        self.enter_destination_airport(self.destination_airport)
        self.choose_oneway()
        self.enter_departure_date()
        self.start_search()
        self.sort()
        self.scrape_flight_data()
        self.save_results()
        self.stop_driver()

    def accept_cookies(self):
        """
        Attempts to close the cookie consent banner on the website if present.
        This function waits for the cookie consent banner's accept button to be clickable and then clicks it.
        Logs success or error in the operation.
        """
        try:
            accept_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "cm-acceptAll"))
            )
            accept_button.click()  # Click the accept button on the cookie consent banner
            self.random_sleep(3, 15)  # Random sleep to mimic human delay
            self.log_to_csv('INFO', 'Accepted cookies successfully')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error accepting cookies')


    def enter_departure_airport(self, airport):
        """
        Inputs the departure airport into the search form.

        Parameters:
            airport (str): The name of the departure airport to be entered.

        This function waits for the departure airport input field to be visible, clicks it,
        clears any existing input, enters the new airport, and selects it from the dropdown.
        Logs success or error in the operation.
        """
        try:
            departure_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/div[2]/div[4]/div/div/div[2]/div/div/div[2]/div[1]/div/section/div[2]/div[1]/div/div/form/div[2]/div[1]/div[1]/div[1]/div/div[1]/div[1]/div[1]/input'))
            )
            departure_button.click()  # Focus on the input field
            self.random_sleep(3, 15)  # Random sleep to mimic human delay
            departure_button.send_keys(Keys.COMMAND + 'a')  # Select existing input
            departure_button.send_keys(airport)  # Enter new airport
            self.random_sleep(3, 15)  # Random sleep to mimic human delay
            departure_button.send_keys(Keys.ARROW_DOWN)
            departure_button.send_keys(Keys.ENTER)
            self.log_to_csv('INFO', f'Entered departure airport: {airport}')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering departure airport')

    def enter_destination_airport(self, airport):
        """
        Inputs the destination airport into the search form.

        Parameters:
            airport (str): The name of the destination airport to be entered.

        This function waits for the destination airport input field to be visible, clears any previous input,
        enters the new airport, and selects it from the dropdown. Logs success or error in the operation.
        """
        try:
            destination_button = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, 'flightQuery.flightSegments[0].destinationCode'))
            )
            destination_button.clear()  # Clear existing input
            destination_button.send_keys(airport)  # Enter new airport
            self.random_sleep(3, 15)  # Random sleep to mimic human delay
            destination_button.send_keys(Keys.ARROW_DOWN)
            destination_button.send_keys(Keys.ENTER)
            self.random_sleep(3, 15)  # Random sleep to mimic human delay
            self.log_to_csv('INFO', f'Entered destination airport: {airport}')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering destination airport')

    def choose_oneway(self):
        """
        Chooses the One-Way flight option on the booking form.

        This function waits for the round-trip option to be clickable, clicks it,
        and then selects the One-Way flight option. It logs the outcome of the operation.
        """
        try:
            # Wait for the round-trip option to be clickable and click it
            round_trip_opt = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dcep-tab-control-standalone3-fluge-section"]/div/div/form/div[1]/div/div/div[1]/button'))
            )
            round_trip_opt.click()

            # Wait for the one-way option to be clickable and select it
            one_way = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dcep-tab-control-standalone3-fluge-section"]/div/div/form/div[1]/div/div/div[2]/ul/li[2]'))
            )
            one_way.click()
            self.log_to_csv('INFO', 'Choose One-Way Flight')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error choosing One-Way Flight')

    def enter_departure_date(self):
        """
        Inputs the departure date into the search form by selecting tomorrow's date from the calendar.

        This function sets the locale to English to ensure the date format matches, clicks on the departure date input,
        selects the date from the calendar, and confirms the selection. It logs the outcome of the operation.
        """
        try:
            # Set locale to English to handle date formatting
            locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

            # Format tomorrow's date for selection
            tomorrow_date = (datetime.now() + timedelta(days=1)).strftime("%A, %d %B %Y")
            date_xpath = f"//td[contains(@class, 'CalendarDay') and contains(@class, 'CalendarDay__default') and contains(@aria-label, '{tomorrow_date}')]"

            # Click on the departure date input field
            departure_date_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[4]/div/div/div[2]/div/div/div[2]/div[1]/div/section/div[2]/div[1]/div/div/form/div[2]/div[2]/div/div[1]/div[1]/input'))
            )
            departure_date_input.click()
            time.sleep(5)

            # Select the date from the calendar
            departure_date = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, date_xpath))
            )
            departure_date.click()
            time.sleep(3)

            # Click the continue button to proceed
            continue_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'btn-primary') and contains(@class, 'calendar-footer-continue-button') and @type='button' and span[text()='Weiter']]"))
            )
            continue_button.click()

            self.log_to_csv('INFO', 'Entered departure date')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering departure date')


    def start_search(self):
        """
        Initiates the flight search after all search parameters have been entered.

        This function waits for the search button to become clickable and then initiates the search.
        Logs the status of the search initiation.
        """
        try:
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[4]/div/div/div[2]/div/div/div[2]/div[1]/div/section/div[2]/div[1]/div/div/form/div[2]/div[4]/button'))
            )
            search_button.click()
            time.sleep(10)  # Wait for search results to start loading
            self.log_to_csv('INFO', 'Search started')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error starting search')


    def sort(self):
        """
        Sorts flights from cheapest to most expensive after search results have loaded.

        This function waits for the sort button to become clickable, clicks it, and then selects
        the option to sort by cheapest first. Logs the status of the sorting process.
        """
        time.sleep(10)  # Wait for all elements to be fully loaded

        try:
            sort_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/div[1]/refx-upsell-premium-filtering-pres/div[2]/refx-upsell-premium-sorting-pres/refx-menu/div/a'))
            )
            sort_button.click()

            cheapest_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[4]/div[2]/div/div/div/button[2]'))
            )
            cheapest_option.click()
            self.log_to_csv('INFO', 'Sorted flights from cheapest to most expensive')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error sorting flights')


    def click_details(self):
        """
        Clicks on the details button for the first flight result.

        This function waits for the details button of the first flight result to become clickable,
        then clicks it to view more details. Logs the action of clicking the details.
        """
        try:
            detail_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/mat-accordion/refx-upsell-premium-row-pres[1]/div/div/refx-flight-card-pres/refx-basic-flight-card-layout/div/div/div[1]/div/div[2]/div/refx-flight-details/div/div[2]/a'))
            )
            detail_button.click()
            self.log_to_csv('INFO', 'Clicked details')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error clicking details')


    def extract_time(self, time_string):
        """
        Extracts hours and minutes from a given time string formatted as '{hours}h {minutes}min'.

        Args:
            time_string (str): The time string to parse.

        Returns:
            list: A list containing the extracted hours and minutes.
        """
        try:
            hours_match = re.search(r'(\d+)h', time_string)
            minutes_match = re.search(r'(\d+)min', time_string)
            hours = hours_match.group(1) if hours_match else "00"
            minutes = minutes_match.group(1) if minutes_match else "00"
            return [hours, minutes]
        except Exception as e:
            self.log_to_csv('ERROR', 'Failed to extract time from string')
            return ["00", "00"]

    def get_transit_duration(self, transit_indicator):
        """
        Calculates the total transit duration based on the flight's transit indicator.

        Args:
            transit_indicator (str): The class attribute used to determine the number of stops.

        Returns:
            str: The formatted total transit duration in 'HH:MM' format.
        """
        try:
            if(transit_indicator == "bound-nb-stop-container has-stops has-1-stop"):
                transit_duration_string = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/mat-dialog-container/refx-itinerary-details-dialog-pres/refx-dialog-pres/div/div[2]/div/div/refx-flight-stop-details-pres/div/div/div/div[2]/div/div[2]').text
                transit_hours = self.time_extract(transit_duration_string)[0]
                transit_minutes = self.time_extract(transit_duration_string)[1]
            elif(transit_indicator == "bound-nb-stop-container has-stops"):
                transit_duration_1_string = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/mat-dialog-container/refx-itinerary-details-dialog-pres/refx-dialog-pres/div/div[2]/div/div/refx-flight-stop-details-pres[1]/div/div/div/div[2]/div/div[2]').text
                transit_duration_2_string = self.driver.find_element(By.XPATH, '/html/body/div[4]/div[2]/div/mat-dialog-container/refx-itinerary-details-dialog-pres/refx-dialog-pres/div/div[2]/div/div/refx-flight-stop-details-pres[2]/div/div/div/div[2]/div/div[2]').text
                transit_hours = str(int(self.time_extract(transit_duration_1_string)[0]) + int(self.time_extract(transit_duration_2_string)[0]))
                transit_minutes = str(int(self.time_extract(transit_duration_1_string)[1]) + int(self.time_extract(transit_duration_2_string)[1]))
            if(int(transit_minutes) > 59):
                transit_hours = str(int(transit_hours) + 1)
                transit_minutes = str(int(transit_minutes) - 60)
            if(len(transit_hours) == 1):
                transit_hours = "0" + transit_hours
            transit_duration = transit_hours + ":" + transit_minutes
            self.log_to_csv('INFO', 'Calculated transit duration successfully')
            return transit_duration
        except Exception as e:
            self.log_to_csv('ERROR', 'Error calculating transit duration')
            return "00:00"

    
    def scrape_flight_data(self):
        """
        Scrapes flight data from the search results and stores it.

        This function collects essential details such as travel duration, departure and arrival times,
        flight type, and price, then logs the scraping status.
        """
        time.sleep(10)
        try:
            duration_string = self.driver.find_element(By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/mat-accordion/refx-upsell-premium-row-pres[1]/div/div/refx-flight-card-pres/refx-basic-flight-card-layout/div/div/div[1]/div/div[2]/div/refx-flight-details/div/div[1]/div[1]/div/span[2]').text
            duration_hours = self.time_extract(duration_string)[0]
            if(len(duration_hours) == 1):
                duration_hours = "0" + duration_hours
            duration_minutes = self.time_extract(duration_string)[1]
            travel_duration = duration_hours + ":" + duration_minutes
            departure_time = self.driver.find_element(By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/mat-accordion/refx-upsell-premium-row-pres[1]/div/div/refx-flight-card-pres/refx-basic-flight-card-layout/div/div/div[1]/div/div[1]/div/refx-bound-timeline/div[1]/div[1]/div[1]/div').text
            arrival_time = self.driver.find_element(By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/mat-accordion/refx-upsell-premium-row-pres[1]/div/div/refx-flight-card-pres/refx-basic-flight-card-layout/div/div/div[1]/div/div[1]/div/refx-bound-timeline/div[1]/div[3]/div[1]/div').text
            flight_type_element = self.driver.find_element(By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/div/refx-upsell-premium-cont/refx-upsell-premium-pres/div/mat-accordion/refx-upsell-premium-row-pres[1]/div/div/refx-flight-card-pres/refx-basic-flight-card-layout/div/div/div[1]/div/div[1]/div/refx-bound-timeline/div[1]/div[2]/div[2]')
            flight_type_indicator = flight_type_element.get_attribute('class')
            if(flight_type_indicator == "bound-nb-stop-container"):
                transit = False
            else:
                transit = True
            price = self.driver.find_element(By.XPATH, '/html/body/app/refx-app-layout/div/div[2]/refx-upsell/refx-basic-in-flow-layout/div/div[6]/div[4]/div/div/refx-calendar-cont/refx-calendar-pres/div/mat-expansion-panel/div/div/refx-carousel/div/ul/li[4]/div/button/span[1]/div[1]/div/refx-price-cont/refx-price/span/span').text
            price = price.replace(".", "")
            price = float(price.replace(",", "."))
            
            if(transit):
                self.click_details()
                transit_duration = self.get_transit_duration(flight_type_indicator)
            else:
                transit_duration = "00:00"
            self.flight_data.append({
                'airline_name': self.airline_name,
                'crawling_date': datetime.now().strftime("%d-%m-%Y"),
                'departure_airport': self.departure_airport,
                'destination_airport': self.destination_airport,
                'date': (datetime.now()+timedelta(days=1)).strftime("%d-%m-%Y"),
                'travel_duration': travel_duration,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'transit': transit,
                'transit_duration': transit_duration,
                'price': price
            })
            self.log_to_csv('INFO', 'Flight data scraped successfully')
        except Exception:
            self.log_to_csv('ERROR', 'Error scraping flight data')