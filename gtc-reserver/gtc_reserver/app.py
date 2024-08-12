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
        # options.add_argument("--headless=new")
        reservation = Reservation( # TODO: Deserialized this from a file; will probably make it easier in the future to accept it as a http request?
            court_type=CourtType.TENNIS,
            acceptableTimes={
                ReservationLength.NINETY: ["7:00pm", "7:30pm"],
                ReservationLength.SIXTY: ["7:00pm", "7:30pm"]
            },
            date="08/16/2024"
        )
        config = ReservationWorkerConfig(
            username=username,
            password=password,
            reservation=reservation,
            webdriver_options=options,
            reservation_start_hour=12,
            reservation_start_minute=30
        )
        
        worker = ReserverWorker(config)
        threads.append((username, worker))
        worker.start()

    while len(threads) > 0:
        # TODO: if worker exits before 12:30, we can assume the thread exited with an error and we should retry it.
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