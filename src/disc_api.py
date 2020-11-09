import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import logging

import queue
import glob_vars



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    logging.info(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        logging.info(guild)


@client.event #receive msg event callback -----------------------
async def on_message(message):
    if message.author == client.user:
        return       
    glob_vars.send_bot_receive_queue(message)
    
@tasks.loop(seconds=0.2)
async def loop():
    try:
        send_item = glob_vars.send_queue.get(False)
        logging.info(send_item)
        channel, content = send_item
        await channel.send(content)
    except queue.Empty:
        send_item = None

def start_api():
    client.run(TOKEN)

loop.start()
