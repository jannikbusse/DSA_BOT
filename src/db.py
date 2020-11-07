import sqlite3
import threading, queue
import time
import random
import discord

t_count = 0
q = queue.Queue() #queue for access calls


def remove_prefix(text, prefix):
    return text[text.startswith(prefix) and len(prefix):]


def createTable(c):
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chars
                (uID, cID)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID PRIMARY KEY, mu, kl, int, ch, ff, ge, ko, kk)''') #int = in!!!!!


def registerChar(c, conn, user, charname):
    cID = user + charname

    c.execute("SELECT EXISTS(SELECT * FROM chartable WHERE cID=?)", (cID,))
    if(c.fetchone()[0]):
       
        return  "error double char ID: " + str(charname)

    c.execute("INSERT INTO chartable VALUES (?, 0, 0, 0, 0 ,0 ,0 ,0 ,0)", (cID,))
    c.execute("INSERT INTO chars VALUES (?, ?)", (user, cID))

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
    c.execute('SELECT * FROM chartable INNER JOIN chars USING(cID) INNER JOIN user USING(uID)')
    rows = c.fetchall()
    for row in rows:
        print(row)

def db_get_char(cID):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM chartable WHERE cID=?",(cID,))
    res = cursor.fetchall()
    conn.close()
    return res

def db_get_char_list(uID):
    
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    cursor.execute("SELECT cID FROM chars WHERE uID =?",(uID,))
    rows = cursor.fetchall()
    res = []
    for row in rows:
        res.append(remove_prefix(row[0], uID))
    conn.close()
    return res
    
def queue_register(msg, charname):
    q.put((0, str(msg.author), charname, msg.channel))

def parse_queue_item(item, c, conn):
    if item[0] == 0: #register call
        uID = item[1]
        charname = item[2]
        channel = item[3]
        success = registerChar(c, conn, uID, charname)
        print(success)


def db_runner(threadName):
    global t_count
    t_count += 1
    print("started " + threadName + " as " + str(t_count) + " thread!")
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    createTable(c)
    conn.commit()

    registerChar(c, conn, "randomRandy", "heral")
    registerChar(c, conn, "randomRandy", "horol")
    registerChar(c, conn, "smuffin", "smuff")
    registerChar(c, conn, "randomRandy", "horol")



    createTable(c)
    conn.commit()
    printTable(c)
    while(True):
        item = q.get()
        parse_queue_item(item,c , conn)
        time.sleep(0.1)

    conn.close()

def queue_adder(threadName): #just a debugger thread!
    print("running")
    #queue_register("smuffin", "smuffelino")
    time.sleep(1)


async def send_msg(channel, content):#fuck this function
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    #result = loop.run_until_complete(channel.send(content))
    await channel.send(content)
    


start_runner()

for i in range(1):#start the debugger thread
    x = threading.Thread(target=queue_adder, args=("adder db",))
    x.start()

