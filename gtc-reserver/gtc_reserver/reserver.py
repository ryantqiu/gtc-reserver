import threading
from gtc_reserver.model import CourtType, ReservationLength, ReservationWorkerConfig
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

RESERVATION_START_HOUR = 12
RESERVATION_START_MINUTE = 30

class ReserverWorker(threading.Thread):
    def __init__(self, config: ReservationWorkerConfig):
        super().__init__()
        self.username = config.username
        self.password = config.password
        self.reservation = config.reservation
        self.driver = webdriver.Chrome(options=config.webdriver_options)
        self.reservation_start_hour = config.reservation_start_hour
        self.reservation_start_minute = config.reservation_start_minute

    def run(self):
        self.login()
        self.navigate_to_reservation_page()
        self.input_reservation_info()
        self.attempt_reservation()

        # uncomment for verifying in non-headless mode
        # time.sleep(20)
        # Close the WebDriver
        self.driver.quit()

    def login(self):
        print(f'{self.username}: attempting to log in...')

        self.driver.get("https://gtc.clubautomation.com/")

        # Input login
        username_field = self.driver.find_element(By.ID, "login")
        username_field.send_keys(self.username) # DOB: 01/01/1990, Address is Sichuan home, Phone is 415-111-1111
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(self.password)
        self.driver.find_element(By.ID, "loginButton").click()
        
        print(f'{self.username}: login completed')

    def navigate_to_reservation_page(self):
        print(f'{self.username}: navigating to reservations page...')
        # Go to reserve a court page
        self.driver.get("https://gtc.clubautomation.com/member/index")
        wait = WebDriverWait(self.driver, timeout=10)
        wait.until(lambda d : self.driver.find_element(By.LINK_TEXT, "Reserve a Court").is_displayed())
        reserve_a_court_button = self.driver.find_element(By.LINK_TEXT, "Reserve a Court")
        reserve_a_court_button.click()
        print(f'{self.username}: navigated to reservations page')

    def input_reservation_info(self):
        self.select_court_type()
        time.sleep(1) # Hacky temp solution; date input becomes stale if we try to input immediately
        self.input_date()
        self.set_search_time_range()

    def select_court_type(self):
        print(f'{self.username}: inputing court type: {self.reservation.court_type}...')

        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID,'location_chosen'))).click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.XPATH,f"//li[text()='{self.reservation.court_type.value}']"))).click()

        print(f'{self.username}: inputed court type: {self.reservation.court_type}')

    def input_date(self):
        print(f'{self.username}: inputing target date...')
        
        date_selector = self.driver.find_element(By.ID, "date")
        date_selector.clear()
        date_selector.send_keys(self.reservation.date)

        print(f'{self.username}: inputed target date')

    def set_search_time_range(self):
        print(f'{self.username}: setting time interval to look for reservations...')

        # Set search interval to all times, from 12:00am to 12:00am
        start_time_dropdown = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "timeFrom_chosen")))
        start_time_dropdown.click()
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "active-result"))).click()

        print(f'{self.username}: set time interval to look for reservations')

    def attempt_reservation(self):
        for length in self.reservation.lengthPreferences:
            if length not in self.reservation.acceptableTimes.keys():
                continue

            self.set_reservation_length(length)

            pause_until(self.reservation_start_hour, self.reservation_start_minute, disabled=False)

            self.search_reservations()

            for time in self.reservation.acceptableTimes[length]:
                if self.attempt_lock_in_reservation(length, time, self.reservation.date):
                    return
    
    def search_reservations(self):
        print(f'{self.username}: searching for reservable slots...')

        search_button = self.driver.find_element(By.NAME, "reserve-court-search")
        wait = WebDriverWait(self.driver, timeout=10000)
        wait.until(lambda d : search_button.is_displayed())
        search_button.click()

        print(f'{self.username}: searched for reservable slots')

    def set_reservation_length(self, length: ReservationLength):
        print(f'{self.username}: selecting reservation length {length.name}...')
        
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH,f"//span[text()='{length.value["button_text"]}']"))).click()

        print(f'{self.username}: selected reservation length {length.name}')

    def attempt_lock_in_reservation(self, length: ReservationLength, time: str, date: str) -> bool:
        print(f'{self.username}: attempting to select and confirm reservation for {length.name} minutes at {time} on {date}...')
        # TODO: Make a confirmation message that we "secured" a reservation

        try:
            # Complete reservation
            WebDriverWait(self.driver, 7).until(EC.element_to_be_clickable((By.LINK_TEXT, time))).click()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "confirm"))).click()
            WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.ID, "button-ok"))).click()
        except:
            print(f'{self.username}: failed to confirm reservation for {length.name} minutes at {time} on {date}')
            return False

        print(f'{self.username}: selected and confirmed reservation for {length.name} minutes at {time} on {date}!')
        return True

"""
Helper method to view all elements on the current screen
"""
def print_all_ids(driver: webdriver):
    ids = driver.find_elements(By.XPATH, '//*[@id]')
    for ii in ids:
        print(ii.get_attribute('id'))

"""
Pauses thread execution until current time is at least start_hour:start_minute
"""
def pause_until(start_hour: int, start_minute: int, disabled=False):
    if disabled:
        return
    
    while True:
        curr_time = time.localtime()
        if curr_time.tm_hour > start_hour or (curr_time.tm_hour == start_hour and curr_time.tm_min >= start_minute):
            break

        if start_hour == curr_time.tm_hour and start_minute - curr_time.tm_min <= 1:
            continue
        else:
            print(f'Checking again in a minute; current time is {curr_time.tm_hour}:{curr_time.tm_min}')
            time.sleep(60)