import requests
from bs4 import BeautifulSoup

def get_sport_data(url: str):
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        betting_lines = [value.text for value in soup.find_all('span', class_='sportsbook-outcome-cell__line')]
        team_ids = [value.text for value in soup.find_all('div', class_='event-cell__name-text')]

        return betting_lines, team_ids