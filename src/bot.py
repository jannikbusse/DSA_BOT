import discord
import queue
import db
import disc_api
import glob_vars
import time, threading
import dice
import helper
import logging
import re

stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"] #careful: in is int in the db!

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False


def received_msg(message):
    parse_msg(message)

def parse_attribute_input(s):
    
    b = re.match(r'\A[a-zA-Z]+\([a-zA-Z]+,[a-zA-Z]+,[a-zA-Z]+\)\Z', s)
    if b:        
        at = re.search(r'([a-zA-Z]*?)\(', s).group(1)
        res = re.search(r'\((.*?)\)',s).group(1)        
        res = res.split(',')
        return(at,res[0], res[1], res[2])

    if re.match(r'\A[a-zA-Z | - | _]+\Z',s):
        return (s, "","","")

    return None


def send_message(channel,content):
    n = 1600
    msgs = [content[i:i+n] for i in range(0, len(content), n)]
    for msg in msgs:
        glob_vars.send_message(channel, msg)
        time.sleep(0.1)

def command_register(message, args):
    if(len(args) < 1):
        send_message(message.channel, "Too few arguments!")
        return
    charname = args[0]
    charNumber = len(db.db_get_char_list(message.author))
    if charNumber >= glob_vars.MAX_CHAR_COUNT:
        send_message(message.channel, "You have too many characters!\nYou can delete one by using the 'delete' command")
        return
    success = db.db_register_char(message.author, charname)
    send_message(message.channel,success)

def command_chars(message):
    chars = db.db_get_char_list(message.author)
    selected = db.get_selected_char(message.author)
    res = ""
    for char in chars:
        if char == selected:
            res +="=>"
        res = res + char.capitalize() + "\n"
    if res == "":
        res = "No chars in database!"
    msg = "You currently have "+ str(len(chars))+"/"+str(glob_vars.MAX_CHAR_COUNT) +" char(s)! \n\n" 
    send_message(message.channel,msg + res)

def command_char(message, args):
    charname = ""

    selected_char = db.get_selected_char(message.author)
    if selected_char == None:
        send_message(message.channel, "User has no character!")  
        return
    if len(args) < 1:
        charname = selected_char
    else:
        charname = args[0]
    if not db.check_char_exists(message.author, charname):
        send_message(message.channel, "This character could not be found in the database!")  
        return

    charEntry, attributeList = db.db_get_char(charname, message.author)
    charEntry = charEntry[0]
    stat = [] 
    for s in glob_vars.stats:
        stat.append(helper.make_str_two_digits(str(helper.attribute_value_from_list(attributeList, s))))
 
    header = "-------------**"+ charname.capitalize() +"**-----------------"
    toprow = "| mu | kl | in | ch | ff | ge | ko | kk |"
    botrow = "| " +stat[0] +" | " +stat[1]+" | " +stat[2]+" | " +stat[3]+" | " +stat[4]+" | " +stat[5]+" | " +stat[6]+" | " +stat[7]+" |\n\n"

    attributes_print = "**Attributes** ("+ str(db.get_attribute_number(charname, message.author))+"/"+ str(glob_vars.MAX_ATTRIBUTE_COUNT) +"): \n"
    for attribute in filter(lambda x: not x[0] in glob_vars.stats, attributeList):
        dependency_print = ""
        if not attribute[2] == "":
            dependency_print = "("+attribute[2]+","+attribute[3]+","+attribute[4]+")"
        attributes_print += str(attribute[0]) + dependency_print+"  " + str(attribute[1]) + "\n"

    send_message(message.channel, header+"\n"+toprow+"\n"+botrow+ attributes_print)

def command_delete(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_remove_char(charname, message.author)
    send_message(message.channel, success)

def command_update(message, args):
    out = ""
    if not db.check_user_has_char(message.author):
        send_message(message.channel, "User has no character!")
        return

    for i in range(len(args))[::2]:
        s = parse_attribute_input(args[i]) 
        if s == None:
            send_message(message.channel, "Oops, wrong arguments for " + args[i])
            return

        if i+1 < len(args):            
            if not is_int(args[i+1]):
                out +=  "arg for **"+ s[0] +"** has to be an integer!\n"
                continue
            attributeValue = int(args[i+1])

            out +=  db.db_update_attribute(message.author, s, attributeValue) + "\n"#first param is "attribute"
        else:
            send_message(message.channel, "Oops, too few arguments for " + s[0])
            return

    send_message(message.channel, out)

def command_selected(message):
    selected = db.get_selected_char(message.author)
    if selected == None:
        send_message(message.channel, "User has no character!")
        return
    send_message(message.channel, "Selected char for user " + str(message.author) + ": " + selected)

def command_select(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    charname = args[0]
    success = db.db_select_char(message.author, charname)
    send_message(message.channel, success)

def command_roll(message, s, args):
    s = helper.remove_prefix(s, "roll")
    s = helper.remove_prefix(s, "r")
    if(len(args) < 1):
        s = "w20"
    res = dice.simulate_dice(s)
    send_message(message.channel, res)

def command_rd(message, args):
    if len(args) != 3 and len(args) != 4 and len(args) != 1:
        send_message(message.channel, "Wrong syntax!\n/rd <stat> <stat> <stat> <talent - optional>")
        return
    if not db.check_user_has_char(message.author):
        send_message(message.channel, "User has no character!")
        return
    
    cID = db.get_selected_char(message.author)
    

    charEntry = db.db_get_char(cID, message.author)
    if len(args) == 1:
        attribute = db.get_attribute(cID,message.author, args[0])
        if attribute == None:
            send_message(message.channel, "Oops, this attribute was not found on **"+cID +"**" )
            return
        if(attribute[6] == "" or attribute[4] == "" or attribute[5] == "" ):
            send_message(message.channel, "Oops, **"+attribute[2]+"** has no dependencies at the moment!" )
            return
        args[0] = attribute[4]
        args.append(attribute[5])
        args.append(attribute[6])
        args.append(attribute[2])    
    res = dice.roll_dsa(args, charEntry)
    send_message(message.channel, res)

def command_set_prefix(message, args):
    if(len(args) < 1):
        send_message(message.channel, "too few arguments!")
        return
    success = db.db_set_prefix(message.guild, args[0])
    send_message(message.channel, success)

def command_remove(message, args):
    selected =  db.get_selected_char(message.author)
    if selected == None:
        send_message(message.channel, "User has no character selected!")
        return
    out = ""
    for arg in args:
        if arg not in glob_vars.stats:
            out += db.db_remove_attribute(selected, message.author, arg) + "\n"
    send_message(message.channel, out)

def command_rename(message, args):#FIX DATABASE FIRST!!
    send_message(message.channel, "This function is not available because my database has been set up very poorly!")
    return
    if len(args) < 2:
        send_message(message.channel, "Too few arguments!")
    currentName = args[0]
    newName = args[1]
    if not db.check_char_exists(message.author, currentName):
        send_message(message.channel, currentName + " could not be found!")
        return
    if db.check_char_exists(message.author, newName):
        send_message(message.channel, newName + " is already in use by one of your characters!")
        return
    success = db.db_rename_character(currentName, message.author, newName)
    send_message(message.channel, success)

def command_help(message, args):
    send_message(message.channel, glob_vars.HELP_MESSAGE)



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

    elif(s.startswith("remove")):
        command_remove(message, args)

    elif(s.startswith("update")):#/update in <int> ch <y> ...
        command_update(message, args)  

    elif(s.startswith("selected")):#/select <charname>
        command_selected(message)

    elif(s.startswith("select")):
        command_select(message,args)
    
    elif(s.startswith("rd ")):
        command_rd(message, args)

    elif(s.startswith("r")): 
        command_roll(message,s ,args)

    elif(s.startswith("prefix")):
        command_set_prefix(message, args)

    elif(s.startswith("rename")):#FIX DATABASE FIRST!!
        command_rename(message, args)

    elif(s.startswith("help")):
        command_help(message, args)

        



def check_queue():
    try:
        send_item = glob_vars.bot_receive_queue.get(False)  
        if send_item.content == "exit":
            glob_vars.terminate = True
        received_msg(send_item)
    except queue.Empty:
        send_item = None

def start_bot():
    
    logging.info("Started bot!")
    db.init_db()
    while(not glob_vars.terminate):
        time.sleep(0.05)
        check_queue()
        

logging.basicConfig(level=logging.INFO, filename="log.txt", filemode="a+",
format="%(asctime)-15s %(levelname)-8s %(message)s")
x = threading.Thread(target=start_bot)
x.start()
disc_api.start_api()