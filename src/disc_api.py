import os
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv

import queue
import glob_vars



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
client = discord.Client()

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        print(guild)


@client.event #receive msg event callback -----------------------
async def on_message(message):
    if message.author == client.user:
        return   
    if message.content.startswith(glob_vars.prefix):
        glob_vars.send_bot_receive_queue(message)
    
@tasks.loop(seconds=0.2)
async def loop():
    try:
        send_item = glob_vars.send_queue.get(False)
        print(send_item)
        channel, content = send_item
        await channel.send(content)
    except queue.Empty:
        send_item = None

def start_api():
    client.run(TOKEN)
    print("started")

loop.start()
