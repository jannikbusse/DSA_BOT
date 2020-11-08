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
        args = s.split()[1:] #whitespaces cant be in charnames because of this
        if(len(args) < 1):
            await send_message("too few arguments!", message.channel)
        db.queue_register(message, args[0])

    if(s.startswith("/chars")):
        db.queue_charlist(message, message.author)     

    if(s.startswith("/delete")):
        args = s.split()[1:]
        if(len(args) < 1):
            await send_message("too few arguments!", message.channel)
        db.queue_delete_char(message, message.author, args[0])

    await send_message("parsing .. " + message.content, message.channel)


