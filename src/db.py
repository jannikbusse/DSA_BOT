import sqlite3
import threading, queue
import time
import random
import discord
import glob_vars
from glob_vars import db_queue as q

conn = None
c = None

def check_char_exists(uID, charname):
    cID = str(uID) + str(charname)
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE cID=?)", (cID,))
    if(c.fetchone()[0]):
        return True
    return False     

def check_user_has_char(uID):
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE uID=?)",(uID,))
    if(c.fetchone()[0]):
        return True
    return False    

def check_user_exists(uID):
    c.execute("SELECT EXISTS(SELECT * FROM user WHERE uID=?)", (uID,))
    if(c.fetchone()[0]):
        return True
    return False     
def get_selected_char(uID):
    c.execute("SELECT sChar FROM user WHERE uID=?", (uID,))
    selected = c.fetchone()[0] #get cID from selected char   
    return selected

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


def createTable():
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID PRIMARY KEY, uID, mu, kl, int, ch, ff, ge, ko, kk)''') #int = in!!!!!


def db_register_char(user, charname):
    cID = user + charname

    if (check_char_exists(user, charname)):
        return  "error double char ID: " + str(charname)

    c.execute("INSERT INTO chartable VALUES (?, ?, 0, 0, 0, 0 ,0 ,0 ,0 ,0)", (cID, user))
    

    if not check_user_exists(user):
        c.execute("INSERT INTO user VALUES (?, ?)", (user, cID))

    conn.commit()
    return "Registered successfully"

def printTable():
    print("\ntable:")
    c.execute('SELECT * FROM chartable INNER JOIN user USING(uID)')
    rows = c.fetchall()
    for row in rows:
        print(row)

def db_get_char(cID):
 
    c.execute("SELECT * FROM chartable WHERE cID=?",(cID,))
    res = c.fetchall()
    return res

def db_get_char_list(uID):    

    c.execute("SELECT cID FROM chartable WHERE uID =?",(uID,))
    rows = c.fetchall()
    res = []
    for row in rows:
        res.append(remove_prefix(row[0], uID))
    return res

def db_remove_char(uID, charname):
    cID = str(uID) + str(charname)
    res = "Trying to remove char - something happened!"
    if not check_char_exists(uID, charname):
        return "char could not be found!"
    c.execute("DELETE FROM chartable WHERE cID =?",(cID,))   
    res = "char has been deleted!" 
    if not check_user_has_char(uID):
        c.execute("DELETE FROM user WHERE uID =?",(uID,))
        res = "char has been deleted. User was deleted aswell!"
    elif get_selected_char(c, uID) == cID:
        next_selected = db_get_char_list(uID)[0]
        db_get_char(c, next_selected)
        res = "char has been deleted - new selected char: " + next_selected

    conn.commit()
    return res

def db_update_stats(uID, stat, statnumber):
    if not check_user_exists(uID):
       return "User has no character selected!"
    selected = get_selected_char(uID)
    c.execute("UPDATE chartable SET "+stat+"=? WHERE cID=?",(statnumber,selected))#pray that there is no exploit where stat can be manipulated outside of allowed values!!
    conn.commit()
    return "updated " + stat + " sucessfully: " + str(statnumber)

def db_select_char(uID, charname):
    cID = uID + charname
    if not check_char_exists(uID, charname):
        return "Could not find char in database!"
    c.execute("UPDATE user SET sChar=? WHERE uID=?",(cID,uID))
    conn.commit()
    return "Selected " + charname + " successfully!"

    
def queue_register(msg, charname):
    q.put((0, msg.channel, str(msg.author), charname))

def queue_charlist(msg, uID):
    q.put((1,msg.channel, str(msg.author)))

def queue_delete_char(msg, uID, charname):
    q.put((2,msg.channel, str(uID), str(charname)))

def queue_update_stats(msg, uID, stat, statnumber):
    q.put((3,msg.channel, str(uID), str(stat), statnumber))

def queue_select_char(msg, uID, charname):
    q.put((4,msg.channel, str(uID), str(charname)))

def queue_get_selected(msg, uID):
    q.put((5,msg.channel, str(uID)))

def parse_queue_item(item):
    channel = item[1]
    uID = item[2]

    if item[0] == 0: #register call
        charname = item[3]
        success = db_register_char(uID, charname)
        glob_vars.send_message(channel,success)
    if item[0] ==1:#list chars call
        chars = db_get_char_list(uID)
        res = ""
        for char in chars:
            res = res + char + "\n"
        if res == "":
            res = "No chars in database!"
        glob_vars.send_message(channel,res)
    if item[0] ==2: #delete call
        charname = item[3]
        success = db_remove_char(uID, charname)
        glob_vars.send_message(channel, success)

    if item[0] ==3: #statchange
        stat = item[3]
        statnumber = item[4]
        success = db_update_stats(uID, stat, statnumber)
        glob_vars.send_message(channel, success)

    if item[0] ==4:#select char
        charname = item[3]
        success = db_select_char(uID, charname)
        glob_vars.send_message(channel, success)

    if item[0] ==5:#print selected
        selected = get_selected_char(uID)
        glob_vars.send_message(channel, "Selected char for user " + uID + ": " + remove_prefix(selected,uID))

def db_runner_update():

    try:
        item = q.get(False)
        parse_queue_item(item)
    except queue.Empty:
        pass


def init_db():
    print("started db!")    
    global conn, c
    conn = sqlite3.connect('DSA_base.db')
    c = conn.cursor()
    createTable()
    conn.commit()

    db_register_char("randomRandy", "heral")
    db_register_char("randomRandy", "horol")
    db_register_char("smuffin", "smuff")
    db_register_char("randomRandy", "horol")

    printTable()

def close_db():
    conn.close()

def queue_adder(threadName): #just a debugger thread!
    print("running")
    #queue_register("smuffin", "smuffelino")
    time.sleep(1)



for i in range(1):#start the debugger thread
    x = threading.Thread(target=queue_adder, args=("adder db",))
    x.start()

