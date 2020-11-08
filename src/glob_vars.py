import queue
send_queue = queue.Queue() #global


def send_message(channel, content):
    send_queue.put((channel, content))