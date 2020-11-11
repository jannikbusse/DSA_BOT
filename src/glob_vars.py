import queue

terminate = False

MAX_ATTRIBUTE_COUNT = 100
MAX_CHAR_COUNT = 10

send_queue = queue.Queue() 
bot_receive_queue = queue.Queue()
stats = ["mu","kl","in","ch","ff","ge", "ko", "kk"]

prefix = '/'

def send_bot_receive_queue(msg):
    bot_receive_queue.put((msg))

def send_message(channel, content):
    send_queue.put((channel, content))

