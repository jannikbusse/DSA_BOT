import discord
import queue
import db
import glob_vars

async def received_msg(message):
    await parse_msg(message)



async def send_message(content, channel):
    await channel.send(content)

async def parse_msg(message):
    s = message.content.lower()
    
    if(s.startswith("/register")):
        args = s.split()[1:]
        db.queue_register(message, args[0])

    if(s.startswith("/chars")):
        db.queue_charlist(message, message.author)
       

    await send_message("parsing .. " + message.content, message.channel)


