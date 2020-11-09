import discord
import queue
import db
import disc_api
import glob_vars
import time, threading
import dice

stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"] #careful: in is int in the db!

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def received_msg(message):
    parse_msg(message)

def update_stats(message, args):
    for i in range(len(args)):
        s = args[i] 
        if s in stats and i+1 < len(args):            
            if is_int(args[i+1]):
                if s == "in" :
                    s = "int"
                db.queue_update_stats(message, message.author, s, args[i+1])
            else:
                send_message(message.channel, "Wrong arg for " + s +": " + args[i+1])



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
    elif(s.startswith("/update")):
        args = s.split()[1:]
        update_stats(message, args)

    elif(s.startswith("/r")): #TODO gar kein bock...
        args = s.split()[1:]
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        dice.simulate_dice(args[0])

    elif(s.startswith("/selected")):
        db.queue_get_selected(message, message.author)
    elif(s.startswith("/select")):
        args = s.split()[1:]
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        db.queue_select_char(message, message.author, args[0])
        


    send_message( message.channel, "parsing .. " + message.content)

def check_queue():
    try:
        send_item = glob_vars.bot_receive_queue.get(False)       
        received_msg(send_item)
    except queue.Empty:
        send_item = None

def start_bot():
    print("Started bot!")
    db.init_db()
    while(True):
        time.sleep(0.2)
        check_queue()
        db.db_runner_update()


x = threading.Thread(target=start_bot)
x.start()
disc_api.start_api()