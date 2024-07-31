from dataclasses import dataclass
from selenium import webdriver
from enum import Enum


class ReservationLength(Enum):
    NINETY = {"length": 90, "button_text": "90 Min"}
    SIXTY = {"length": 60, "button_text": "60 Min"}
    FIFTY = {"length": 50, "button_text": "50 Min"}
    THIRTY = {"length": 30, "button_text": "30 Min"}

class CourtType(Enum):
    TENNIS = "Tennis"
    PICKLEBALL = "Pickleball / Mini Tennis"

@dataclass
class Reservation():
    court_type: CourtType
    date: str
    time: str
    length: ReservationLength

@dataclass
class ReservationWorkerConfig():
    username: str
    password: str
    reservation: str
    webdriver_options: webdriver.IeOptions
    reservation_start_hour: int = 12
    reservation_start_minute: int = 30
