import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot import *

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
    print("msg")
    if message.author == client.user:
        return   
    await received_msg(message)
    
        #await message.channel.send(response)


client.run(TOKEN)