import sqlite3
import threading, queue
import time
import random
import discord
import helper
import logging
import glob_vars

conn = None
c = None

def check_char_exists(uID, cID):
    uID = str(uID)
    cID = str(cID)
    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE cID=? AND uID = ?)", (cID, uID))
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
    
def check_char_has_attribute(cID, uID, attribute):
    cID = str(cID)
    uID = str(uID)
    attribute = str(attribute)
    c.execute("SELECT EXISTS(SELECT * FROM attributes WHERE cID=? AND uID =? AND attribute=?)", (cID, uID, attribute) )
    if(c.fetchone()[0]):
        return True
    return False   

def get_attribute_number(cID, uID):
    cID = str(cID)
    uID = str(uID)
    c.execute("SELECT COUNT(*) FROM attributes WHERE cID = ? AND uID = ?", (cID, uID))
    res = c.fetchone()[0]
    return res-8

def get_selected_char(uID):
    uID = str(uID)
    c.execute("SELECT sChar FROM user WHERE uID=?", (uID,))
    selected = c.fetchone() #get cID from selected char   
    if selected == None:
        return None
    return selected[0]

def get_attribute(cID, uID, attributeName):
    cID = str(cID)
    uID = str(uID)
    attributeName = str(attributeName)
    res = None
    c.execute("SELECT * FROM attributes WHERE cID=? AND uID = ? AND attribute=?",(cID, uID,attributeName))
    res = c.fetchone()
    return res

def get_attribute_list(cID, uID):
    cID = str(cID)
    uID = str(uID
    )
    c.execute("SELECT attribute, value, dep1, dep2, dep3 FROM attributes WHERE cID = ? AND uID = ? ORDER BY length(attribute) DESC",(cID,uID))
    res = c.fetchall()
    return res


def create_attribute_from_char(cID,uID, attribute, value):
    cID = str(cID)
    uID = str(uID)
    
    c.execute("INSERT INTO attributes VALUES (?, ?, ?, ?, ?, ?, ?)", (cID, uID, str(attribute[0]), value, str(attribute[1]),str(attribute[2]),str(attribute[3])))
    conn.commit()

def update_attribute_from_char(cID, uID, attribute, value):
    uID = str(uID)
    
    c.execute("UPDATE attributes SET value =?, dep1 =?, dep2 =?, dep3=? WHERE cID=? AND uID =? AND attribute =?",(value, str(attribute[1]), str(attribute[2]),str(attribute[3]),cID, uID, str(attribute[0])))
    conn.commit()

def createTable():
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS server
                (sID PRIMARY KEY, prefix )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID , uID , PRIMARY KEY(cID, uID) )''') #int = in!!!!!

    c.execute('''CREATE TABLE IF NOT EXISTS attributes
                (cID, uID, attribute, value, dep1, dep2, dep3)''') #int = in!!!!!


def db_update_attribute(uID, attribute, value):#attribute = [name,dep1,dep2,dep3]
    selected = get_selected_char(uID)
   
    already_exists = check_char_has_attribute(selected, uID, attribute[0])

    if not already_exists:
        attributeNumber = get_attribute_number(selected, uID)
        if attributeNumber < glob_vars.MAX_ATTRIBUTE_COUNT:
            create_attribute_from_char(selected, uID, attribute, value)
            return "**"+str(attribute[0]) +"** has been created with **" + str(value) + "**!"
        else:
            return "**"+str(attribute[0]) +"** has not been created! **"+selected+"** is too powerful!\nYou can remove attributes by using the'remove' command!" 

    else:
        update_attribute_from_char(selected,uID, attribute, value)
        return "**"+str(attribute[0]) +"** has been set to **" + str(value) + "**!"

def db_rename_character(cID, uID, newCID):#TODO BAD IDAE BECAUSE GARBAGE DATABASE
    cID = str(cID)
    uID = str(uID)
    newCID = str(newCID)
    c.execute("UPDATE chartable SET cID =? WHERE cID=? AND uID = ?",(newCID,cID, uID))
    conn.commit()
    return "**"+cID.capitalize() + "** has been changed to **" + newCID.capitalize() +"**!"


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
    cID = str(charname)
    if (check_char_exists(user, charname)):
        return  "error double char ID: " + str(charname)

    c.execute("INSERT INTO chartable VALUES (?, ?)", (cID, user))
    for a in glob_vars.stats:
        create_attribute_from_char(cID, user, [a,"","",""], 0)

    if not check_user_exists(user):
        c.execute("INSERT INTO user VALUES (?, ?)", (user, cID))

    conn.commit()
    return "Registered successfully"

def db_remove_attribute(cID, uID, attribute):
    uID = str(uID)
    cID = str(cID)
    attribute = str(attribute)
    c.execute("DELETE FROM attributes WHERE cID =? AND uID = ? AND attribute = ?",(cID, uID, attribute))  
    conn.commit()
    return "Removed the attribute **" + attribute +"**!"


def printTable():
    print("\ntable:")
    c.execute('SELECT * FROM chartable INNER JOIN user USING(uID)')
    rows = c.fetchall()
    for row in rows:
        print(row)

def db_get_char(cID, uID):
    uID = str(uID)
    cID = str(cID)
    print(uID + "  und charid ist: " +cID)
    c.execute("SELECT * FROM chartable WHERE cID=? AND uID = ?",(cID,uID))
    res = c.fetchall()
    attributes = get_attribute_list(cID, uID)

    return (res, attributes)

def db_get_char_list(uID):    
    uID = str(uID)
    c.execute("SELECT cID FROM chartable WHERE uID =?",(uID,))
    rows = c.fetchall()
    res = []
    for row in rows:
        res.append(row[0])
    return res

def db_remove_char(cID, uID):
    uID = str(uID)
    cID = str(cID)
    res = "Trying to remove char - something happened!"
    if not check_char_exists(uID, cID):
        return "char could not be found!"
    c.execute("DELETE FROM chartable WHERE cID =? AND uID = ?",(cID, uID))  
    c.execute("DELETE FROM attributes WHERE cID =? AND uID = ?",(cID, uID))   
 
    res = "char has been deleted!" 
    if not check_user_has_char(uID):
        c.execute("DELETE FROM user WHERE uID =?",(uID,))
        res = "char has been deleted. User was deleted aswell!"
    elif get_selected_char(uID) == cID:
        next_selected = db_get_char_list(cID, uID)[0]
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

def db_select_char(uID, cID):
    uID = str(uID)
    cID = str(cID)
   
    if not check_char_exists(uID, cID):
        return "Could not find char in database!"
    c.execute("UPDATE user SET sChar=? WHERE uID=?",(cID,uID))
    conn.commit()
    return "Selected " + cID + " successfully!"

    

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

