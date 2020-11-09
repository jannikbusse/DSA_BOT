import queue

send_queue = queue.Queue() 
bot_receive_queue = queue.Queue()

def send_bot_receive_queue(msg):
    bot_receive_queue.put((msg))

def send_message(channel, content):
    send_queue.put((channel, content))

