from dataclasses import dataclass
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