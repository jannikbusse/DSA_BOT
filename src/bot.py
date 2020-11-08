import discord
import queue
import db
import disc_api
import glob_vars
import time, threading
import dice

def received_msg(message):
    parse_msg(message)




def send_message(channel,content):
    glob_vars.send_message(channel, content)

def parse_msg(message):
    s = message.content.lower()
    
    if(s.startswith("/register")):
        args = s.split()[1:] #whitespaces cant be in charnames because of this
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        db.queue_register(message, args[0])

    elif(s.startswith("/chars")):
        db.queue_charlist(message, message.author)     

    elif(s.startswith("/delete")):
        args = s.split()[1:]
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        db.queue_delete_char(message, message.author, args[0])

    elif(s.startswith("/r")):
        args = s.split()[1:]
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        dice.simulate_dice(args[0])
        


    send_message( message.channel, "parsing .. " + message.content)

def check_queue():
    try:
        send_item = glob_vars.bot_receive_queue.get(False)       
        received_msg(send_item)
    except queue.Empty:
        send_item = None

def start_bot():
    print("Started bot!")
    while(True):
        time.sleep(0.2)
        check_queue()

x = threading.Thread(target=start_bot)
x.start()
disc_api.start_api()