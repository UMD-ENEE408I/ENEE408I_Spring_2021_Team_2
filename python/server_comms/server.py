#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.options
import string
import threading 


from tornado.options import define, options

define("port", default=5001, help="run on the given port", type=int)

class Thread (threading.Thread):
   def __init__(self, threadID, name, counter, foo):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
      self.foo = foo

   def run(self):
      self.foo() 
      print("runnig" + self.name)

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/", MainHandler)]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MainHandler, self).__init__(*args, **kwargs)
        self.jeopardyThread = Thread(2, "jeopardy", 2, start_jeopardy)


    def check_origin(self, origin):
        return True

    def open(self):
        logging.info("A client connected.")

    def on_close(self):
        logging.info("A client disconnected")

    def on_message(self, message):
        logging.info("message: {}".format(message))
        # self.write_message("HI")
        if (message.lower() == "start jeopardy"):
            self.jeopardyThread.start()

        if (message.lower() == "stop jeopardy"):
            if self.jeopardyThread.isAlive():
                stop_jeopardy()
                self.jeopardyThread.join()
            else:
                print("Jeopardy thread does not exist")
            

def start_jeopardy():
    print("OMG WE ARE PLAYING JEOPARDY")

def stop_jeopardy():
    print("NOOOO I WANT TO KEEP PLAYIN")

def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    # mainThread = Thread(1, "main", 1, main)
    # mainThread.start()
    main()

