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


def send_message(channel,content):
    glob_vars.send_message(channel, content)

def command_register(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_register_char(message.author, charname)
    send_message(message.channel,success)

def command_chars(message):
    chars = db.db_get_char_list(message.author)
    res = ""
    for char in chars:
        res = res + char + "\n"
    if res == "":
        res = "No chars in database!"
    send_message(message.channel,res)

def command_delete(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_remove_char(message.author, charname)
    send_message(message.channel, success)

def command_update(message, args):
    for i in range(len(args)):
        s = args[i] 
        if s in stats and i+1 < len(args):            
            if is_int(args[i+1]):
                if s == "in" :
                    s = "int"
                               
                statnumber = args[i+1]
                success = db.db_update_stats(message.author, s, statnumber)
                send_message(message.channel, success)
            else:
                send_message(message.channel, "Wrong arg for " + s +": " + args[i+1])

def command_selected(message):
    selected = db.get_selected_char(message.author)
    send_message(message.channel, "Selected char for user " + str(message.author) + ": " + db.remove_prefix(selected,str(message.author)))

def command_select(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_select_char(message.author, charname)
    send_message(message.channel, success)

def parse_msg(message):
    s = message.content.lower()
    send_message( message.channel, "parsing .. \"" + message.content + "\" ...")

    if(s.startswith("/register")): #/register <charname>
        args = s.split()[1:] #whitespaces cant be in charnames because of this
        command_register(message, args)

    elif(s.startswith("/chars")): #/chars
        command_chars(message)     

    elif(s.startswith("/delete")):#/delete <charname>
        args = s.split()[1:]
        command_delete(message, args)

    elif(s.startswith("/update")):#/update in <int> ch <y> ...
        args = s.split()[1:]
        command_update(message, args)  

    elif(s.startswith("/selected")):#/select <charname>
        command_selected(message)

    elif(s.startswith("/select")):
        args = s.split()[1:]        
        command_select(message,args)

    elif(s.startswith("/r")): #TODO gar kein bock...
        args = s.split()[1:]
        if(len(args) < 1):
            send_message(message.channel, "too few arguments!")
            return
        dice.simulate_dice(args[0])
        



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
        


x = threading.Thread(target=start_bot)
x.start()
disc_api.start_api()