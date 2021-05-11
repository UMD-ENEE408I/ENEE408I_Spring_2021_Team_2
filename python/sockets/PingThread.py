from threading import Thread
import time
import websockets
import json

class PingThread(Thread):
    def __init__(self, ws):
        Thread.__init__(self)
        self.run_thread = True
        self.ws = ws

    def run(self):
        self.ping_msg = {"type": "ping"}
        while self.run_thread == True:
            #send ping messsage
            self.ws.send(self.ping_msg)
            time.sleep(5)
    
    def stop_thread(self):
        self.run_thread = False

    def set_name(self, name):
        self.name = name