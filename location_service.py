import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LocationService:
    def __init__(self):
        self.base_url = "https://api.countrystatecity.in/v1/"
        self.headers = {
            "X-CSCAPI-KEY": os.getenv("LOCATION_SECRET"),
        }

    def all_countries(self):
        response = requests.get(f"{self.base_url}countries", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def all_states_by_country(self, ciso):
        response = requests.get(f"{self.base_url}countries/{ciso}/states", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def all_cities_in_state_and_country(self, ciso, siso):
        response = requests.get(f"{self.base_url}countries/{ciso}/states/{siso}/cities", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def all_cities_in_country(self, ciso):
        response = requests.get(f"{self.base_url}countries/{ciso}/cities", headers=self.headers)
        response.raise_for_status()
        return response.json()
