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
        "cfb": os.getenv('URL_CFB'),
        "cbb": os.getenv('URL_NCAAM')
    }
    try:
        with closing(sqlite3.connect(os.getenv('DB_NAME'))) as con, \
                closing(con.cursor()) as cur:
            
            cur.execute('DELETE FROM match')
            cur.execute('DELETE FROM sqlite_sequence WHERE name = "match"')
            print('match table purged in bls.db')

            for sport_id, url in sport_urls.items():
                betting_lines, team_ids, event_start_times = await get_sport_data(url)
                matches = build_match_list(betting_lines, team_ids, event_start_times)

                query = f'INSERT INTO match (sport_id, start_time, home_team_id, home_team_spread, away_team_id, away_team_spread, total) VALUES (?,?,?,?,?,?,?)'
                values = [(sport_id, match.start_time, match.home_team_id, match.home_spread, match.away_team_id, match.away_spread, match.total)
                    for match in matches
                ]

                for match in matches:
                    print(f"trying to delete {match}")
                    del match

                cur.executemany(query, values)
                con.commit()
                print(f'match table populated with {sport_id} matches.')

            print("all matches populated.")

    except sqlite3.Error as e:
        print(f"Database Error: {e}")
    except Exception as e:
       print(f"Unexpected Error: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    scrape_sport_data.start()

@bot.command()
async def get_data(ctx, sport_id, sport_team: str = None, *args):
    try:
        with closing(sqlite3.connect(os.getenv('DB_NAME'))) as con, \
                closing(con.cursor()) as cur:
            
            query = 'SELECT * FROM match WHERE sport_id = ?'
            values = [sport_id]

            if sport_team:
                query += ' AND (home_team_id LIKE ? OR away_team_id LIKE ?)'
                values.extend([f"%{sport_team}%", f"%{sport_team}"])

            cur.execute(query, values)
            results = cur.fetchall()

            if results:
                formatted_results = "\n".join(
                    f"Start Time: {row[2]}, Home: {row[3]} ({row[4]}), "
                    f"Away: {row[5]} ({row[6]}), Total: {row[7]}" 
                    for row in results
                    )
                await ctx.send(f"Query Results:\n```\n{formatted_results}\n```")
            else:
                await ctx.send("No matches found for the given criteria.")

    except sqlite3.Error as e:
        await ctx.send(f"Database error: {e}")
    except Exception as e:
        await ctx.send(f"Unexpected error: {e}")   

load_dotenv()
bot.run(os.getenv('BOT_TOKEN'))