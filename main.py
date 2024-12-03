import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
from match import build_match_list
from stats import get_sport_data

intents=discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def get_data(ctx, sport_id: str = None, sport_team: str = None, *args):
    sport_urls = {
        "nfl": os.getenv('URL_NFL'),
        "nba": os.getenv('URL_NBA'),
        "nhl": os.getenv('URL_NHL'),
        "cfb" or "ncaaf": os.getenv('URL_CFB'),
        "ncaam" or "ncaab": os.getenv('URL_NCAAM')
    }

    url = sport_urls.get(sport_id.lower())
    if not url:
        await ctx.send(f"Invalid sport_id: {sport_id}. Please specify 'nfl', 'nba', or 'nhl'.")
        return

    betting_lines, team_ids, event_start_times = await get_sport_data(url)
    matches = build_match_list(betting_lines, team_ids, event_start_times)

    if sport_team:
        team_found = next(
        (match for match in matches 
         if sport_team.lower() in match.home_team_id.lower() or 
            sport_team.lower() in match.away_team_id.lower()), 
        None
    )
        if team_found:
            msg = team_found
        else:
            msg = f"No match found for team: {sport_team}"
    else:
        msg = "\n".join(str(match) for match in matches)

    await ctx.send(msg)

load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))