from dataclasses import dataclass
import threading
from gtc_reserver.model import CourtType, Reservation, ReservationLength
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time

RESERVATION_START_HOUR = 12
RESERVATION_START_MINUTE = 30

class ReserverWorker(threading.Thread):
    def __init__(self, username: str, password: str, reservation: Reservation, webdriver_options):
        super().__init__()
        self.username = username
        self.password = password
        self.reservation = reservation
        self.driver = webdriver.Chrome(options=webdriver_options)

    def run(self):
        login(self.driver, self.username, self.password)
        navigate_to_reservation_page(self.driver)
        input_reservation_info(self.driver, self.reservation.date, self.reservation.length, self.reservation.court_type)
        pause_until(RESERVATION_START_HOUR, RESERVATION_START_MINUTE, disabled=True)
        search_reservation_times(self.driver)
        select_reservation(self.driver, self.reservation.time)
        time.sleep(20)
        # Close the WebDriver
        self.driver.quit()

def login(driver: webdriver, username: str, password: str):
    print("attempting to log in...")

    driver.get("https://gtc.clubautomation.com/")

    # Input login
    username_field = driver.find_element(By.ID, "login")
    username_field.send_keys(username) # DOB: 01/01/1990, Address is Sichuan home, Phone is 415-111-1111
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    driver.find_element(By.ID, "loginButton").click()
    
    print("login completed")

def navigate_to_reservation_page(driver: webdriver):
    print("navigating to reservations page...")
    # Go to reserve a court page
    driver.get("https://gtc.clubautomation.com/member/index")
    wait = WebDriverWait(driver, timeout=10)
    wait.until(lambda d : driver.find_element(By.LINK_TEXT, "Reserve a Court").is_displayed())
    reserve_a_court_button = driver.find_element(By.LINK_TEXT, "Reserve a Court")
    reserve_a_court_button.click()
    print("navigated to reservations page")

def input_reservation_info(driver: webdriver, date: str, length: ReservationLength, court_type: CourtType):
    select_court_type(driver, court_type)  
    time.sleep(1) # Hacky temp solution; date input becomes stale if we try to input immediately
    input_date(driver, date)
    set_search_time_range(driver)
    set_reservation_length(driver, length)

def pause_until(start_hour: int, start_minute: int, disabled=False):
    if disabled:
        return
    
    while True:
        curr_time = time.localtime()
        if curr_time.tm_hour == start_hour and curr_time.tm_min == start_minute:
            break

        if start_hour == curr_time.tm_hour and start_minute - curr_time.tm_min <= 1:
            continue
        else:
            print(f'Checking again in a minute; current time is {curr_time.tm_hour}:{curr_time.tm_min}')
            time.sleep(60)

def select_court_type(driver: webdriver, court_type: CourtType):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID,'location_chosen'))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,f"//li[text()='{court_type.value}']"))).click()

def input_date(driver: webdriver, date: str):
    print("inputing target date...")
    
    date_selector = driver.find_element(By.ID, "date")
    date_selector.clear()
    date_selector.send_keys(date)

    print("inputed target date")

def set_search_time_range(driver: webdriver):
    print("setting time interval to look for reservations...")

    # Set search interval to all times, from 12:00am to 12:00am
    start_time_dropdown = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "timeFrom_chosen")))
    start_time_dropdown.click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, "active-result"))).click()

    print("setting time interval to look for reservations")

def set_reservation_length(driver: webdriver, length: ReservationLength):
    print("selecting reservation length...")
    
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,f"//span[text()='{length.value["button_text"]}']"))).click()

    print("selected reservation length")

def search_reservation_times(driver: webdriver):
    print("searching for reservable slots...")

    search_button = driver.find_element(By.NAME, "reserve-court-search")
    wait = WebDriverWait(driver, timeout=10000)
    wait.until(lambda d : search_button.is_displayed())
    search_button.click()

    print("searched for reservable slots")

def select_reservation(driver: webdriver, time: str):
    print("selecting and confirming reservation...")

    # Complete reservation
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.LINK_TEXT, time))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "confirm"))).click()
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "button-ok"))).click()

    print("selected and confirmed reservation!")

def print_all_ids(driver: webdriver):
    ids = driver.find_elements(By.XPATH, '//*[@id]')
    for ii in ids:
        print(ii.get_attribute('id'))