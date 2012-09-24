# -*- coding:utf-8
#!/usr/bin/env python
from AuthBot import AuthBot as Bot
from GlobalConfig import *
import IRCFonts
import os

if __name__ == '__main__':    
    if CHANGE_RUNTIME_USER:
        os.setgid(GID)
        os.setuid(UID)
    
    bot = Bot()
    bot.connect()
    for channel in STARTUP_CHANNELS:
        bot.join(channel)
    bot.start()
    bot.stop()
