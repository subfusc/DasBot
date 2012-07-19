# -*- coding:utf-8
#!/usr/bin/env python
from AuthBot import AuthBot as Bot
from GlobalConfig import *
import os
from threading import Timer

def delayed_say(bot, channel, msg):
    bot.msg(channel, msg)

if __name__ == '__main__':    
    if CHANGE_RUNTIME_USER:
        os.setgid(GID)
        os.setuid(UID)
    
    bot = Bot()
    bot.connect()
    bot.join("#iskbot")
    bot.msg("#iskbot", "I AM HERE!")
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(5, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    # Timer(4, delayed_say, [bot, "#iskbot", "Testing synchronization of sockets outbound thing."]).start()
    bot.start()
    bot.stop()
