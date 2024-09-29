from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from base_crawler import BaseCrawler
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os
import csv

class KLMCrawler(BaseCrawler):

    def __init__(self, departure_airport, destination_airport, date):
        """
        Initializes the KLMCrawler with specific travel details.

        Parameters:
            departure_airport (str): The name of the departure airport.
            destination_airport (str): The name of the destination airport.
            date (str): The departure date in a string format.
        """
        url = "https://www.klm.de/search/advanced"
        airline_name = "KLM"
        self.departure_airport = departure_airport
        self.destination_airport = destination_airport
        self.date = date
        self.flight_data = []
        super().__init__(url, airline_name)

    def run(self):
        """
        Executes the sequence of web scraping steps.
        """
        print(f"------------------ {self.airline_name}: {self.departure_airport} - {self.destination_airport} ------------------")
        self.start_driver_klm()
        self.open_url()
        self.accept_cookies()
        self.select_one_way_flight()
        self.click_blank_space()
        self.enter_departure_airport(self.departure_airport)
        self.enter_destination_airport(self.destination_airport)
        self.enter_departure_date(self.date)
        self.verify_and_fill_fields()
        self.search_flights() 
        self.select_filter_option()
        selected_index = self.check_and_select_economy()  
        price = self.extract_price() 
        
        if price:
            self.click_button_in_opened_tab(selected_index)  

            flight_details = self.extract_flight_details()
            if flight_details:
                flight_details['price'] = price
                flight_details['airline_name'] = self.airline_name
                flight_details['crawling_date'] = datetime.now().strftime('%Y-%m-%d')
                flight_details['departure_airport'] = self.departure_airport
                flight_details['destination_airport'] = self.destination_airport
                flight_details['date'] = self.date

                self.save_results(flight_details)
            else:
                self.log_to_csv('ERROR', 'Flight details could not be extracted.')
        else:
            self.log_to_csv('ERROR', 'Price could not be extracted.')

        self.stop_driver()  

    def accept_cookies(self):
        """
        Handles the acceptance of cookies on the website.

        Waits for the 'Accept Cookies' button to become clickable, clicks it, and logs the process.
        In case of failure, logs the error.
        """
        try:
            decline_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#accept_cookies_btn"))
            )
            decline_button.click()
            time.sleep(3)
            self.log_to_csv('INFO', 'Accepted cookies successfully')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error accepting cookies')

    def click_blank_space(self):
        """
        Clicks on an empty area of the page to ensure no dropdowns or overlays are active.

        Attempts to click the body of the page to clear any active elements, and logs the process.
        Logs an error if the click fails.
        """
        try:
            self.driver.find_element(By.TAG_NAME, 'body').click()
            self.log_to_csv('INFO', 'Clicked on an empty area.')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error clicking on the empty area.')


    def select_one_way_flight(self):
        """
        Selects the 'One Way' flight option from the dropdown.

        Waits for the dropdown to become clickable, selects the 'One Way' option, and logs the action.
        In case of failure, logs the error.
        """
        try:
            dropdown_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#mat-input-0"))
            )
            dropdown_button.click()
            one_way_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#mat-input-0 > option:nth-child(2)"))
            )
            one_way_option.click()
            time.sleep(5)
            self.log_to_csv('INFO', 'One way flight selected successfully.')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error selecting one way flight.')

    def enter_departure_airport(self, airport):
        """
        Enters the departure airport into the designated input field.

        Attempts to click the field, clears it, and enters the airport code, followed by confirmation.
        Verifies the input and logs the process. If an error occurs, it logs the issue.
        """
        try:
            for _ in range(2):  
                departure_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-input-5"]'))
                )
                departure_button.click()
                time.sleep(1)  

            departure_button.clear()
            departure_button.send_keys(airport)
            departure_button.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value((By.XPATH, '//*[@id="mat-input-5"]'), airport)
            )
            self.log_to_csv('INFO', f'Entered departure airport: {airport}')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering departure airport')

    def enter_destination_airport(self, airport):
        """
        Enters the destination airport into the designated input field.

        Attempts to click the field, clears it, and enters the airport code, followed by confirmation.
        Verifies the input and logs the process. If an error occurs, it logs the issue.
        """
        try:
            for _ in range(2):  
                destination_input_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="mat-input-6"]'))
                )
                destination_input_field.click()
                time.sleep(1) 

            destination_input_field.clear()
            destination_input_field.send_keys(airport)
            destination_input_field.send_keys(Keys.RETURN)
            WebDriverWait(self.driver, 10).until(
                EC.text_to_be_present_in_element_value((By.XPATH, '//*[@id="mat-input-6"]'), airport)
            )
            self.log_to_csv('INFO', f'Entered destination airport: {airport}')
        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering destination airport')

    def enter_departure_date(self, date):
        """
        Handles the selection of a departure date from a date picker.

        Opens the date picker, selects the specified day, confirms the selection, and logs the process.
        In case of an error, it logs the issue.
        """
        try:
            date_picker_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="bw-search-widget-expandable"]/div/bw-datepicker/bwc-form-input-container/div/label/mat-form-field/div[1]/div/div[2]/bwc-date-picker-toggle-button/button/span[3]'))
            )
            date_picker_button.click()
            self.log_to_csv('INFO', 'Opened date picker successfully')

            day, month, year = date.split('.')
            day_xpath = f'//*[@id="bwc-day_{year}_{int(month)-1}_{int(day)}"]'
            day_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, day_xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", day_button)
            day_button.click()

            confirm_button_xpath = '/html/body/div[3]/div[2]/div[2]/bwc-calendar/div/div[3]/button[2]'
            confirm_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, confirm_button_xpath))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", confirm_button)
            self.driver.execute_script("arguments[0].click();", confirm_button)
            WebDriverWait(self.driver, 10).until(
                EC.invisibility_of_element_located((By.XPATH, confirm_button_xpath))
            )
            self.log_to_csv('INFO', f'Entered departure date: {date}')

        except Exception as e:
            self.log_to_csv('ERROR', 'Error entering departure date')

    def verify_and_fill_fields(self):
        """
        Verifies that the departure and destination airport fields are filled.

        If any of the fields are empty, it refills them using the provided data and logs the process.
        Logs errors if the fields cannot be verified or filled.
        """
        departure_airport_value = self.driver.find_element(By.XPATH, '//*[@id="mat-input-5"]').get_attribute('value')
        destination_airport_value = self.driver.find_element(By.XPATH, '//*[@id="mat-input-6"]').get_attribute('value')

        if not departure_airport_value:
            self.log_to_csv('ERROR', 'Departure airport field is empty. It will be filled again.')
            self.enter_departure_airport(self.departure_airport)
        else:
            self.log_to_csv('INFO', 'Departure airport field is filled')

        if not destination_airport_value:
            self.log_to_csv('ERROR', 'Destination field is empty. It will be filled again.')
            self.enter_destination_airport(self.destination_airport)
        else:
            self.log_to_csv('INFO', 'Destination field is filled')

    def search_flights(self):
        """
        Initiates a flight search and waits for the search results page to load.

        Uses a retry mechanism to attempt the search up to a maximum number of attempts.
        Verifies that required fields are filled before proceeding with the search. Logs the process and errors.
        """
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                self.verify_and_fill_fields()

                search_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="bw-search-widget-form-15hCmh4vxh"]/div/div[2]/div[2]/button'))
                )
                self.driver.execute_script("arguments[0].click();", search_button)
                self.log_to_csv('INFO', 'Pressed Enter to search for flights')

                search_results = WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/bw-app/bwc-page-template/mat-sidenav-container/mat-sidenav-content/div/main/div/bwsfe-search-result'))
                )
                self.log_to_csv('INFO', 'Successfully navigated to the search results page')
                return  

            except Exception as e:
                self.log_to_csv('ERROR', 'Attempt {attempt+1}/{max_attempts} - Error during flight search')
                time.sleep(5) 

        self.log_to_csv('ERROR', f'Flight search could not be completed after {max_attempts} attempts.')

    def select_filter_option(self):
        """
        Selects a specific filter option from a dropdown menu.

        Waits for the dropdown to be clickable, selects the desired option, and logs the action.
        In case of failure, logs the error.
        """
        try:
            dropdown = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="bw-flight-list-result-filters__select-0"]'))
            )
            dropdown.click()

            option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="bw-flight-list-result-filters__select-0"]/option[1]'))
            )
            option.click()
            self.log_to_csv('INFO', 'Option selected from the dropdown')

            time.sleep(5)
        except Exception as e:
            self.log_to_csv('ERROR', 'Error selecting filter option')

    def check_and_select_economy(self):
        """
        Checks and selects the economy class option for a flight.

        Iterates over flight options until it finds the economy class, selects it, and logs the action.
        Logs errors and continues to the next option if the current one fails.
        """
        index = 1
        while True:
            try:
                container_xpath = f'//*[@id="flight{index}cabinClassCardTabECONOMY"]'
                clickable_element_xpath = f'//*[@id="flight{index}cabinClassCardTabECONOMY"]/div/div'

                container = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, container_xpath))
                )

                clickable_element = container.find_element(By.XPATH, clickable_element_xpath)
                if clickable_element:
                    clickable_element.click()
                    self.log_to_csv('INFO', 'Economy option selected successfully')
                    time.sleep(5) 
                    return index  

            except Exception as e:
                self.log_to_csv('ERROR', f'Error processing flight {index}')  
                index += 1  
                continue 

    def extract_price(self):
        """
        Extracts the flight price from the displayed elements on the page.

        Scrolls the page to make sure the price element is visible, then extracts and logs the price.
        Logs an error if no price element is found or if extraction fails.
        """
        try:
            self.driver.execute_script("window.scrollBy(0, 250);")
            time.sleep(2)  

            mat_tab_contents = self.driver.find_elements(By.XPATH, '//*[contains(@id, "mat-tab-content-")]')
        
            for mat_tab_content in mat_tab_contents:
                if mat_tab_content.is_displayed():

                    first_tab = mat_tab_content.find_element(By.XPATH, './div/section/div/bws-flight-upsell-item[1]')
                    price_container = first_tab.find_element(By.XPATH, './div/div[1]')
                    price_element = price_container.find_element(By.XPATH, './bws-flight-upsell-price/span')
                    price = price_element.text
                
                    self.log_to_csv('INFO', 'Price extracted successfully')
                    return price
        
            self.log_to_csv('ERROR', 'No visible mat-tab-content element found')  
            return None

        except Exception as e:
            self.log_to_csv('ERROR', 'Error extracting the price')  
            return None

    def click_button_in_opened_tab(self, index):
        """
        Clicks a specific button within an opened flight tab.

        Uses a dynamic index to locate the button, clicks it, and logs the process.
        If clicking fails, logs the error.
        """
        try:
            button_xpath = f'/html/body/bw-app/bwc-page-template/mat-sidenav-container/mat-sidenav-content/div/main/div/bwsfe-search-result/div/section/bwsfe-search-result-list/section/ol/li[{index}]/bwsfc-flight-offer/div/div[1]/div[2]/button'
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, button_xpath))
            )
            self.driver.execute_script("arguments[0].click();", button)
            self.log_to_csv('INFO', 'Clicked button in the opened tab successfully')

            time.sleep(5)
        
        except Exception as e:
            self.log_to_csv('ERROR', 'Error clicking the button in the opened tab')              

    def extract_flight_details(self):
        """
        Extracts flight details including total flight duration, landing time, departure time, and transit duration.

        Verifies the presence of these elements, extracts the relevant details, and logs the information.
        Logs errors if any details could not be extracted.
        """
        try:
            total_flight_duration_xpath = '//*[@id="mat-mdc-dialog-0"]/div/div/bwsfc-flight-details/mat-dialog-content/div/bwsfc-flight-details-flight-info/div[4]/span'
            landing_time_xpath = '//*[@id="mat-mdc-dialog-0"]/div/div/bwsfc-flight-details/mat-dialog-content/ol/li[2]/div/div[3]/bwsfc-segment-nodes/div/bwsfc-segment-station-node[2]/div[2]/span'
            departure_time_xpath = '//*[@id="mat-mdc-dialog-0"]/div/div/bwsfc-flight-details/mat-dialog-content/ol/li[2]/div/div[3]/bwsfc-segment-nodes/div/bwsfc-segment-station-node[1]/div[2]/span'
            transit_time_xpath = '//*[@id="mat-mdc-dialog-0"]/div/div/bwsfc-flight-details/mat-dialog-content/ol/li[1]/div[2]/div[2]'

            total_flight_duration_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, total_flight_duration_xpath))
            )
            total_flight_duration = total_flight_duration_element.text
            self.log_to_csv('INFO', 'Total flight duration extracted successfully')

            landing_time_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, landing_time_xpath))
            )
            landing_time = landing_time_element.text
            self.log_to_csv('INFO', 'Landing time extracted successfully')

            departure_time_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, departure_time_xpath))
            )
            departure_time = departure_time_element.text
            self.log_to_csv('INFO', 'Departure time extracted successfully')

            transit = False
            transit_time = None
            try:
                transit_time_element = self.driver.find_element(By.XPATH, transit_time_xpath)
                if transit_time_element:
                    transit = True
                    transit_time = transit_time_element.text
                    self.log_to_csv('INFO', 'Transit time extracted successfully')
            except:
                self.log_to_csv('ERROR', 'Transit time could not be extracted')              

            return {
                'travel_duration': total_flight_duration,
                'arrival_time': landing_time,
                'departure_time': departure_time,
                'transit': transit,
                'transit_duration': transit_time
            }

        except Exception as e:
            self.log_to_csv('ERROR', 'Error extracting flight details')              
            return None
        
    def format_duration(self, duration):
        """
        Formats the flight duration from the provided string into HH:MM format.

        Processes the duration string, removes unnecessary text, and converts hours and minutes to the correct format.
        """
        if "Transferzeit:" in duration:
            duration = duration.replace("Transferzeit:", "").strip()
        duration = duration.replace('h', ' ').replace('min', '').strip()
        hours, minutes = duration.split()
        return f"{int(hours):02d}:{int(minutes):02d}"

    def save_results(self, flight_details):
        """
        Saves the scraped data to a CSV file.
        """
        results_file = f'results/results_{self.airline_name}.csv'
        fieldnames = [
            'airline_name', 'crawling_date', 'departure_airport', 
            'destination_airport', 'date', 'travel_duration', 
            'departure_time', 'arrival_time', 'transit', 
            'transit_duration', 'price'
        ]

        if not os.path.exists('results'):
            os.makedirs('results')

        flight_details['travel_duration'] = self.format_duration(flight_details['travel_duration'])
        flight_details['transit_duration'] = self.format_duration(flight_details['transit_duration'])
        flight_details['date'] = flight_details['date'].replace('.', '-')
        flight_details['price'] = float(flight_details['price'].replace(' EUR', '').replace('.', '').replace(',', '.'))

        file_exists = os.path.isfile(results_file)
        mode = 'a' if file_exists else 'w'

        with open(results_file, mode, newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(flight_details)

        self.log_to_csv('INFO', f'Results saved to {results_file}')
