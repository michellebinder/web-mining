from austrian_airlines_crawler import AustrianAirlinesCrawler
from klm_crawler import KLMCrawler
from qatar_airways_crawler import QatarAirwaysCrawler
from datetime import datetime, timedelta
from base_crawler import BaseCrawler
import time
import os
import csv

def main():

    def count_lines_in_file(filepath):
        """ Helper function to count the lines in a file """
        if not os.path.exists(filepath):
            return 0
        with open(filepath, 'r') as file:
            return sum(1 for _ in file)

    def run_crawler_with_expected_results(crawler, results_file_path, expected_count):
        """ Function to run the crawler and verify that the expected number of results has been added """
        initial_line_count = count_lines_in_file(results_file_path)
        crawler.run()
        current_line_count = count_lines_in_file(results_file_path)
        new_lines_added = current_line_count - initial_line_count

        # Check if the expected number of new lines has been added
        attempts = 0
        max_attempts = 3  # Maximum number of attempts
        while new_lines_added < expected_count and attempts < max_attempts:
            print(f"Expected {expected_count} new lines, found {new_lines_added}. Repeating the crawling process...")
            time.sleep(10)  # Short pause to circumvent potential temporary issues
            crawler.run()
            current_line_count = count_lines_in_file(results_file_path)
            new_lines_added = current_line_count - initial_line_count
            attempts += 1

    tomorrow = datetime.now() + timedelta(days=1)
    qatar_date = tomorrow.strftime('%Y-%m-%d')  
    klm_date = tomorrow.strftime('%d.%m.%Y')  

    departure_airport = 'Frankfurt'
    qatar_departure_airport = 'FRA'
    qatar_destinations = ['BER', 'HAM', 'LHR', 'IST', 'DXB']
    austrian_klm_destinations = [
        'Berlin', 'Hamburg', 'München', 'London', 
        'Palma de Mallorca', 'Istanbul', 'Dubai', 'New York', 'Shanghai'
    ]

    qatar_results_file_path = "results/results_QatarAirways.csv"
    klm_results_file_path = "results/results_KLM.csv"
    austrian_results_file_path = "results/results_AustrianAirlines.csv"

    ## CRAWLER FOR KLM ### 
    print("------------------ Started crawling for KLM Airlines ------------------")
    for destination in austrian_klm_destinations:
        klm_crawler = KLMCrawler(departure_airport, destination, klm_date)
        run_crawler_with_expected_results(klm_crawler, klm_results_file_path, 1)
    print("------------------ Finished crawling for KLM Airlines ------------------")

    ## CRAWLER FOR QATAR AIRWAYS ### 
    print("------------------ Started crawling for Qatar Airways ------------------")
    for destination in qatar_destinations:
        qatar_crawler = QatarAirwaysCrawler(qatar_departure_airport, destination, qatar_date)
        run_crawler_with_expected_results(qatar_crawler, qatar_results_file_path, 1)
    print("------------------ Finished crawling for Qatar Airways ------------------")

    # ### CRAWLER FOR AUSTRIAN AIRLINES ### 
    print("------------------ Started crawling for Austrian Airlines ------------------")
    for destination in austrian_klm_destinations:
        austrian_crawler = AustrianAirlinesCrawler(departure_airport, destination)
        run_crawler_with_expected_results(austrian_crawler, austrian_results_file_path, 1)
    print("------------------ Finished crawling for Austrian Airlines ------------------")

if __name__ == "__main__":
    main()