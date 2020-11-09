import queue

send_queue = queue.Queue() 
bot_receive_queue = queue.Queue()

prefix = '/'

def send_bot_receive_queue(msg):
    bot_receive_queue.put((msg))

def send_message(channel, content):
    send_queue.put((channel, content))

