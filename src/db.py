import sqlite3
import threading, queue
import time
import random

t_count = 0
q = queue.Queue() #queue for access calls

def createTable(c):
    c.execute('''CREATE TABLE IF NOT EXISTS user
                (uID PRIMARY KEY, sChar )''')

    c.execute('''CREATE TABLE IF NOT EXISTS chars
                (uID, cID)''')

    c.execute('''CREATE TABLE IF NOT EXISTS chartable
                (cID PRIMARY KEY, mu, kl, int, ch, ff, ge, ko, kk)''') #int = in!!!!!

# Insert a row of data

def registerChar(c, user, charname):
    cID = user + charname
    c.execute("INSERT INTO chartable VALUES (?, 0, 0, 0, 0 ,0 ,0 ,0 ,0)", (cID,))
    c.execute("INSERT INTO chars VALUES (?, ?)", (user, cID))

    c.execute("SELECT EXISTS(SELECT * FROM user WHERE uID=?)", (user,))
    if(not c.fetchone()[0]):
        print((user, cID))
        c.execute("INSERT INTO user VALUES (?, ?)", (user, cID))

def start_runner():
    if t_count <= 0:   
        x = threading.Thread(target=db_runner, args=("thread db",))
        x.start()
    return

def printTable(c):
    print("\nchartable:")
    c.execute('SELECT * FROM chartable INNER JOIN chars USING(cID) INNER JOIN user USING(uID)')
    rows = c.fetchall()
    for row in rows:
        print(row)

def db_runner(threadName):
    global t_count
    t_count += 1
    print("started " + threadName + " as " + str(t_count) + " thread!")
    conn = sqlite3.connect('example.db')
    c = conn.cursor()

    createTable(c)
    #registerChar(c, "threadacc", "threadchar")
    conn.commit()
    printTable(c)
    while(True):
        item = q.get()
        print(q.qsize())

    conn.close()

def queue_adder(threadName):
    print("running")
    while(True):
        time.sleep(1)
        q.put(random.random())
       

for i in range(100):
    x = threading.Thread(target=queue_adder, args=("adder db",))
    x.start()

start_runner()