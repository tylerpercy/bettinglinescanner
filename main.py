import discord
import asyncio
import os
import sqlite3
from contextlib import closing
from dotenv import load_dotenv
from discord.ext import commands, tasks
from match import build_match_list
from stats import get_sport_data

intents=discord.Intents.all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents)

@tasks.loop(seconds=60)
async def scrape_sport_data():
    sport_urls = {
        "nfl": os.getenv('URL_NFL'),
        "nba": os.getenv('URL_NBA'),
        "nhl": os.getenv('URL_NHL'),
        "cfb" or "ncaaf": os.getenv('URL_CFB'),
        "cbb" or "ncaab": os.getenv('URL_NCAAM')
    }
    with closing(sqlite3.connect(os.getenv('DB_NAME'))) as con, con, \
            closing(con.cursor()) as cur:
        cur.execute('DELETE FROM match')
        print('match table purged in bls.db')
        for sport_id, url in sport_urls.items():
            betting_lines, team_ids, event_start_times = await get_sport_data(url)
            matches = build_match_list(betting_lines, team_ids, event_start_times)
            for match in matches:
                query = f'INSERT INTO match (sport_id, start_time, home_team_id, home_team_spread, away_team_id, away_team_spread, total) VALUES (?,?,?,?,?,?,?)'
                values = (sport_id, match.start_time, match.home_team_id, match.home_spread, match.away_team_id, match.away_spread, match.total)
                cur.execute(query, values)
            print(f'match table populated with {sport_id} matches.')
        print("all matches populated.")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    scrape_sport_data.start()

@bot.command()
async def get_data(ctx, sport_id: str = None, sport_team: str = None, *args):
    sport_urls = {
        "nfl": os.getenv('URL_NFL'),
        "nba": os.getenv('URL_NBA'),
        "nhl": os.getenv('URL_NHL'),
        "cfb" or "ncaaf": os.getenv('URL_CFB'),
        "cbb" or "ncaab": os.getenv('URL_NCAAM')
    }

    url = sport_urls.get(sport_id.lower())
    if not url:
        msg = f"Invalid sport_id: {sport_id}.\nPlease select a sport from the list below:```- NBA\n- NFL\n- NHL\n- CFB/NCAAF\n- CBB/NCAAB\n```"
        await ctx.send(msg)
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