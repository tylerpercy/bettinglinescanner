import discord
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands

class match:

    home_team_id: str
    home_spread: str
    away_team_id: str
    away_spread: str
    total: float

    def __init__(self, homeTeamId, homeSpread, awayTeamId, awaySpread, total):
        self.home_team_id = homeTeamId
        self.home_spread = homeSpread
        self.away_team_id = awayTeamId
        self.away_spread = awaySpread
        self.total = total

intents=discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

def format_data(betting_lines, team_ids):

    matches = []

    grouped_lines = [betting_lines[i:i+4][:-1] for i in range(0, len(betting_lines), 4)]
    grouped_teams = [team_ids[i:i+2] for i in range(0, len(team_ids), 2)]

    for lines, teams in zip(grouped_lines, grouped_teams):
        #print(f"{teams[0]}: {lines[0]}")
        #print(f"{teams[1]}: {lines[2]}")
        #print(f"Total: {lines[1]}")
        #print("")
        matches.append(match(teams[1], lines[2], teams[0], lines[0], lines[1]))

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command()
async def get_nfl(ctx):
    url = 'https://sportsbook.draftkings.com/leagues/football/nfl'
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    betting_lines = [value.text for value in soup.find_all('span', class_='sportsbook-outcome-cell__line')]
    team_ids = [value.text for value in soup.find_all('div', class_='event-cell__name-text')]

    format_data(betting_lines, team_ids)

load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))
