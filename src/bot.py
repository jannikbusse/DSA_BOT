import discord
import db

async def received_msg(message):
    await parse_msg(message)



async def send_message(content, channel):
    await channel.send(content)

async def parse_msg(message):
    s = message.content.lower()
    
    if(s.startswith("/register")):
        args = s.split()[1:]
        db.queue_register(message, args[0])
        await send_message(args, message.channel)

    if(s.startswith("/chars")):
        chars = db.db_get_char_list(str(message.author))
        res = ""
        for char in chars:
            res = res + char + "\n"
        await send_message(res, message.channel)

    


