from bs4 import BeautifulSoup
import aiohttp
from datetime import datetime, timedelta

async def get_sport_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                raise ValueError(f"Failed to fetch data: {response.status}")
            text = await response.text()

    soup = BeautifulSoup(text, 'html.parser')

    betting_lines = [value.text for value in soup.find_all('span', class_='sportsbook-outcome-cell__line')]
    team_ids = [value.text for value in soup.find_all('div', class_='event-cell__name-text')]
    event_start_times =  [
        (lambda time_str: (datetime.strptime(time_str, "%I:%M%p") - timedelta(hours=5)).strftime("%I:%M%p"))
        (time) for time in [value.text for value in soup.find_all('span', class_='event-cell__start-time')][::2]
    ]

    return betting_lines, team_ids, event_start_times

async def get_match_data():
    pass