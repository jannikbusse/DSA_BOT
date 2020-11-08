import sqlite3
import threading, queue
import time
import random
import discord
import glob_vars
from glob_vars import db_queue as q

t_count = 0# threadcount (dumb way to implement singleton...)

def check_char_exists(c, uID, charname):
    cID = str(uID) + str(charname)
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE cID=?)", (cID,))
    if(c.fetchone()[0]):
        return True
    return False     

def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


def createTable(c):
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID PRIMARY KEY, uID, mu, kl, int, ch, ff, ge, ko, kk)''') #int = in!!!!!


def db_register_char(c, conn, user, charname):
    cID = user + charname

    if (check_char_exists(c, user, charname)):
        return  "error double char ID: " + str(charname)

    c.execute("INSERT INTO chartable VALUES (?, ?, 0, 0, 0, 0 ,0 ,0 ,0 ,0)", (cID, user))
    

    c.execute("SELECT EXISTS(SELECT * FROM user WHERE uID=?)", (user,))
    if(not c.fetchone()[0]):
        c.execute("INSERT INTO user VALUES (?, ?)", (user, cID))

    conn.commit()
    return "Registered successfully"

def start_runner():
    if t_count <= 0:   
        x = threading.Thread(target=db_runner, args=("thread db",))
        x.start()
    return

def printTable(c):
    print("\ntable:")
    c.execute('SELECT * FROM chartable INNER JOIN user USING(uID)')
    rows = c.fetchall()
    for row in rows:
        print(row)

def db_get_char(c, cID):
 
    c.execute("SELECT * FROM chartable WHERE cID=?",(cID,))
    res = c.fetchall()
    return res

def db_get_char_list(c, uID):    

    c.execute("SELECT cID FROM chartable WHERE uID =?",(uID,))
    rows = c.fetchall()
    res = []
    for row in rows:
        res.append(remove_prefix(row[0], uID))
    return res

def db_remove_char(c, conn, uID, charname):
    cID = str(uID) + str(charname)
    if not check_char_exists(c, uID, charname):
        return "char could not be found!"
    c.execute("DELETE FROM chartable WHERE cID =?",(cID,))    
    conn.commit()
    return "Following char was deleted: " +charname
    
def queue_register(msg, charname):
    q.put((0, msg.channel, str(msg.author), charname))

def queue_charlist(msg, uID):
    q.put((1,msg.channel, str(msg.author)))

def queue_delete_char(msg, uID, charname):
    q.put((2,msg.channel, str(uID), str(charname)))

def parse_queue_item(item, c, conn):
    channel = item[1]
    uID = item[2]

    if item[0] == 0: #register call
        charname = item[3]
        success = db_register_char(c, conn, uID, charname)
        glob_vars.send_message(channel,success)
    if item[0] ==1:#list chars call
        chars = db_get_char_list(c, uID)
        res = ""
        for char in chars:
            res = res + char + "\n"
        glob_vars.send_message(channel,res)
    if item[0] ==2: #delete call
        charname = item[3]
        success = db_remove_char(c, conn, uID, charname)
        glob_vars.send_message(channel, success)
        


def db_runner(threadName):
    global t_count
    t_count += 1
    print("started " + threadName + " as " + str(t_count) + " thread!")
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    createTable(c)
    conn.commit()

    db_register_char(c, conn, "randomRandy", "heral")
    db_register_char(c, conn, "randomRandy", "horol")
    db_register_char(c, conn, "smuffin", "smuff")
    db_register_char(c, conn, "randomRandy", "horol")


    createTable(c)
    conn.commit()
    printTable(c)
    while(True):
        item = q.get()
        parse_queue_item(item,c , conn)
        time.sleep(0.2)

    conn.close()

def queue_adder(threadName): #just a debugger thread!
    print("running")
    #queue_register("smuffin", "smuffelino")
    time.sleep(1)


start_runner()

for i in range(1):#start the debugger thread
    x = threading.Thread(target=queue_adder, args=("adder db",))
    x.start()

