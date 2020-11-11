import discord
import queue
import db
import disc_api
import glob_vars
import time, threading
import dice
import helper
import logging

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
    n = 1900
    msgs = [content[i:i+n] for i in range(0, len(content), n)]
    for msg in msgs:
        glob_vars.send_message(channel, msg)
        time.sleep(0.1)

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

def command_char(message, args):
    charname = ""
    if not db.check_user_has_char(message.author):
        send_message(message.channel, "User has no character!")
        return
    if len(args) < 1:
        charname = helper.remove_prefix(db.get_selected_char(message.author), str(message.author))
    else:
        charname = args[0]
    charEntry, attributeList = db.db_get_char(message.author, charname)
    charEntry = charEntry[0]
    stat = [] 
    for s in glob_vars.stats:
        stat.append(helper.make_str_two_digits(str(helper.attribute_value_from_list(attributeList, s))))
 
    header = "-------------**"+ charname +"**-----------------"
    toprow = "| mu | kl | in | ch | ff | ge | ko | kk |"
    botrow = "| " +stat[0] +" | " +stat[1]+" | " +stat[2]+" | " +stat[3]+" | " +stat[4]+" | " +stat[5]+" | " +stat[6]+" | " +stat[7]+" |\n\n"
    attributes_print = "**Attributes:** \n"
    for attribute in filter(lambda x: not x[0] in glob_vars.stats, attributeList):
        attributes_print += str(attribute[0]) + "  " + str(attribute[1]) + "\n"

    send_message(message.channel, header+"\n"+toprow+"\n"+botrow+ attributes_print)

def command_delete(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_remove_char(message.author, charname)
    send_message(message.channel, success)

def command_update(message, args):
    out = ""
    for i in range(len(args))[::2]:
        s = args[i] 
        if i+1 < len(args):            
            if not is_int(args[i+1]):
                out +=  "arg for **"+ s +"** has to be an integer!\n"
                continue
            attributeValue = int(args[i+1])

            out +=  db.db_update_attribute(message.author, s, attributeValue) + "\n"#first param is "attribute"
            

    send_message(message.channel, out)

def command_selected(message):
    selected = db.get_selected_char(message.author)
    send_message(message.channel, "Selected char for user " + str(message.author) + ": " + helper.remove_prefix(selected,str(message.author)))

def command_select(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_select_char(message.author, charname)
    send_message(message.channel, success)

def command_roll(message, s, args):
    s = helper.remove_prefix(s, "roll")
    if(len(args) < 1):
        s = "w20"
    res = dice.simulate_dice(s)
    send_message(message.channel, res)

def command_rd(message, args):
    if len(args) != 3 and len(args) != 4:
        send_message(message.channel, "Wrong syntax!\n/rd <stat> <stat> <stat> <talent - optional>")
        return

    if not db.check_user_has_char(message.author):
        send_message(message.channel, "User has no character!")
        return
    charname = helper.remove_prefix(db.get_selected_char(message.author), str(message.author))
    charEntry = db.db_get_char(message.author, charname)
    res = dice.roll_dsa(args, charEntry)
    send_message(message.channel, res)

def command_set_prefix(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    success = db.db_set_prefix(message.guild, args[0])
    send_message(message.channel, success)


def parse_msg(message):
    prefix = db.db_get_prefix(message.guild)

    if str(message.content) == "prefix":
        send_message(message.channel, "The prefix for this server is: "+ prefix)
        return

    if not message.content.startswith(prefix):
        return
    
    s = message.content.lower()
    s = helper.remove_prefix(s, prefix)
    args = s.split()[1:]
    #send_message( message.channel, "parsing .. \"" + message.content + "\" ...") # debug message

    if(s.startswith("register")): #/register <charname>
        command_register(message, args)

    elif(s.startswith("chars")): #/chars
        command_chars(message)     
    
    elif(s.startswith("char")): #/char <charname - optional>        
        command_char(message, args)     

    elif(s.startswith("delete")):#/delete <charname>
        command_delete(message, args)

    elif(s.startswith("update")):#/update in <int> ch <y> ...
        command_update(message, args)  

    elif(s.startswith("selected")):#/select <charname>
        command_selected(message)

    elif(s.startswith("select")):
        command_select(message,args)
    
    elif(s.startswith("rd ")):
        command_rd(message, args)

    elif(s.startswith("roll")): 
        command_roll(message,s ,args)

    elif(s.startswith("prefix")):
        command_set_prefix(message, args)

        



def check_queue():
    try:
        send_item = glob_vars.bot_receive_queue.get(False)       
        received_msg(send_item)
    except queue.Empty:
        send_item = None

def start_bot():
    
    logging.info("Started bot!")
    db.init_db()
    while(True):
        time.sleep(0.2)
        check_queue()
        

logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="a+",
format="%(asctime)-15s %(levelname)-8s %(message)s")
x = threading.Thread(target=start_bot)
x.start()
disc_api.start_api()