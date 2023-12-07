import sqlite3
from os import getenv
from datetime import date

from dotenv import load_dotenv
import discord
from discord.ext import commands


load_dotenv()
TOKEN = getenv('TOKEN')
CHANNEL_ID = int(getenv('CHANNEL_ID'))
DATABASE = getenv('DATABASE')

connection = sqlite3.connect(DATABASE)

intents = discord.Intents.default()
intents.message_content = True
intents.guild_scheduled_events = True

bot = commands.Bot(command_prefix='!', intents=intents)

#@bot.event
#async def on_ready():
    #channel = bot.get_channel(CHANNEL_ID)
    #await channel.send("Connected and ready to determine who's picking the next game!")

# @bot.event
# async def on_scheduled_event_create(event):
#     channel = bot.get_channel(CHANNEL_ID)
#     print(event)
#     await channel.send("Get ready for games! Please join the event before noon the day of if you want to be considered for game picking!")


@bot.command()
async def records(ctx):
    message = ""
    rows = connection.cursor().execute('SELECT * FROM players ORDER BY last_picked ASC')
    for row in rows:
        message += "%s last picked %s \n" % (row[0], row[1])

    await ctx.send(message)

@bot.command()
async def next(ctx, *players):
    if players[0] == 'all':
        players = ['David', 'Lou', 'EJ', 'Lampros', 'Jarad']

    question_marks = "%s" % ("?," * len(players))[:-1]

    next_player = connection.cursor() \
        .execute('SELECT * FROM players WHERE name IN (%s) ORDER BY last_picked ASC' % (question_marks), players) \
        .fetchone()

    if next_player is None:
        await ctx.send("No valid players provided, try again...")
        return

    await ctx.send("%s gets to pick the next game! They last picked %s." % (next_player[0], next_player[1])) 

@bot.command()
async def played(ctx, player):
    connection.cursor() \
        .execute('UPDATE players SET last_picked = ? WHERE name like ?', [date.today(), player])

    await ctx.send('Thanks for playing! %s has been updated' % (player,))

@bot.command()
async def ref(ctx):
    message = "!next PlayerOne PlayerTwo - Accepts space seperated list of players. Please capitalize names.\n"
    message += "!played Picker - Set who picked the last game. Please capitalize names.\n"
    message += "!records - See the underlying data so you can understand why the robot doesn't like you"

    await ctx.send(message)

bot.run(TOKEN)
