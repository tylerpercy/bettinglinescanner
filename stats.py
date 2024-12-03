from bs4 import BeautifulSoup
import aiohttp

async def get_sport_data(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
                if response.status != 200:
                        raise ValueError(f"Failed to fetch data: {response.status}")
                text = await response.text()

        soup = BeautifulSoup(text, 'html.parser')
        betting_lines = [value.text for value in soup.find_all('span', class_='sportsbook-outcome-cell__line')]
        team_ids = [value.text for value in soup.find_all('div', class_='event-cell__name-text')]

        return betting_lines, team_ids