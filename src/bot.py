import discord

async def received_msg(message):
    await parse_msg(message)
    await send_message("hab ich bekommen", message.channel)


async def send_message(content, channel):
    await channel.send(content)

async def parse_msg(message):
    s = message.content.lower()
    
    if(s.startswith("/register")):
        args = s.split()[1:]
        print(args)
        await send_message(args, message.channel)
    


