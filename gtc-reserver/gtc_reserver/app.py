import csv
from selenium import webdriver

from gtc_reserver.reserver import *


def main():
    accounts = read_logins("logins.csv")
    threads = {}

    for username, password in accounts.items():
        options = webdriver.ChromeOptions()
        # Enable headless mode
        # options.add_argument("--headless=new")
        reservation = Reservation(CourtType.TENNIS, "01/16/2024", "7:00am", ReservationLength.THIRTY)
        threads[username] = ReserverWorker(username, password, reservation, options)
        threads[username].start()

    for _, thread in threads.items():
        thread.join()

def read_logins(filepath: str):
    logins = {}
    
    with open(filepath, mode="r") as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if len(row) == 2:
                key, value = row
                logins[key] = value
    
    return logins

if __name__ == "__main__":
    main()