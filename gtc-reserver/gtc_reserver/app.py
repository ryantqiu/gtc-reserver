import csv
from gtc_reserver.model import Reservation
from selenium import webdriver

from gtc_reserver.reserver import *


def main():
    accounts = read_logins("logins.csv")
    threads = []

    for username, password in accounts.items():
        options = webdriver.ChromeOptions()
        # Enable headless mode
        options.add_argument("--headless=new")
        reservation = Reservation(
            CourtType.TENNIS, 
            "08/05/2024", 
            "7:00pm", 
            ReservationLength.NINETY)
        config = ReservationWorkerConfig(
            username,
            password,
            reservation,
            options,
            # 20,
            # 17
        )
        
        worker = ReserverWorker(config)
        threads.append((username, worker))
        worker.start()

    while len(threads) > 0:
        username, worker = threads.pop(0)
        if worker.is_alive():
            threads.append((username, worker))
        else:
            print(f'{username} finished.')

def read_logins(filepath: str):
    print('reading logins...')
    logins = {}
    
    with open(filepath, mode="r") as file:
        csv_reader = csv.reader(file)
        
        for row in csv_reader:
            if len(row) == 2:
                key, value = row
                logins[key] = value
    
    print('logins read')
    return logins

if __name__ == "__main__":
    main()