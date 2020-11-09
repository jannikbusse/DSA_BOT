import sqlite3
import threading, queue
import time
import random
import discord
import helper
import logging

conn = None
c = None

def check_char_exists(uID, charname):
    cID = str(uID) + str(charname)
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE cID=?)", (cID,))
    if(c.fetchone()[0]):
        return True
    return False     

def check_user_has_char(uID):
    uID = str(uID)
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE uID=?)",(uID,))
    if(c.fetchone()[0]):
        return True
    return False    

def check_user_exists(uID):
    c.execute("SELECT EXISTS(SELECT * FROM user WHERE uID=?)", (uID,))
    if(c.fetchone()[0]):
        return True
    return False     

def check_server_exists(sID):
    sID = str(sID)
    c.execute("SELECT EXISTS(SELECT * FROM server WHERE sID=?)", (sID,))
    if(c.fetchone()[0]):
        return True
    return False   
    
def get_selected_char(uID):
    uID = str(uID)
    c.execute("SELECT sChar FROM user WHERE uID=?", (uID,))
    selected = c.fetchone()[0] #get cID from selected char   
    return selected


def createTable():
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS server
                (sID PRIMARY KEY, prefix )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID PRIMARY KEY, uID, mu, kl, int, ch, ff, ge, ko, kk)''') #int = in!!!!!

def db_get_prefix(server):
    sID = str(server.id)
    c.execute("SELECT prefix FROM server WHERE sID=?",(sID,))
    res = c .fetchall()
    if len(res) == 0:
        print("no pre!")
        return '/'
    
    return res[0][0]

def db_set_prefix(server, prefix):
    sID = str(server.id)
    
    prefix = str(prefix)
    if not check_server_exists(sID):
        c.execute("INSERT INTO server VALUES (?, ?)", (sID, prefix))
        conn.commit()
        return "prefix has been created: " + prefix
    c.execute("UPDATE server SET prefix =? WHERE sID=?",(prefix,sID))
    conn.commit()
    return "prefix has been set to: "+prefix    



def db_register_char(user, charname):
    user = str(user)
    charname = str(charname)
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

def db_get_char(uID, charname):
    cID = str(uID) + str(charname)
    c.execute("SELECT * FROM chartable WHERE cID=?",(cID,))
    res = c.fetchall()
    return res

def db_get_char_list(uID):    
    uID = str(uID)
    c.execute("SELECT cID FROM chartable WHERE uID =?",(uID,))
    rows = c.fetchall()
    res = []
    for row in rows:
        res.append(helper.remove_prefix(row[0], uID))
    return res

def db_remove_char(uID, charname):
    uID = str(uID)
    cID = str(uID) + str(charname)
    res = "Trying to remove char - something happened!"
    if not check_char_exists(uID, charname):
        return "char could not be found!"
    c.execute("DELETE FROM chartable WHERE cID =?",(cID,))   
    res = "char has been deleted!" 
    if not check_user_has_char(uID):
        c.execute("DELETE FROM user WHERE uID =?",(uID,))
        res = "char has been deleted. User was deleted aswell!"
    elif get_selected_char(uID) == cID:
        next_selected = db_get_char_list(uID)[0]
        res = "char has been deleted - new selected char: " + next_selected

    conn.commit()
    return res

def db_update_stats(uID, stat, statnumber:int):
    uID = str(uID)
    if not check_user_exists(uID):
       return "User has no character selected!"
    selected = get_selected_char(uID)
    c.execute("UPDATE chartable SET "+stat+"=? WHERE cID=?",(statnumber,selected))#pray that there is no exploit where stat can be manipulated outside of allowed values!!
    conn.commit()
    return "updated " + stat + " sucessfully: " + str(statnumber)

def db_select_char(uID, charname):
    uID = str(uID)
    charname = str(charname)
    cID = uID + charname
    if not check_char_exists(uID, charname):
        return "Could not find char in database!"
    c.execute("UPDATE user SET sChar=? WHERE uID=?",(cID,uID))
    conn.commit()
    return "Selected " + charname + " successfully!"

    

def init_db():
    logging.info("started db!")    
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

