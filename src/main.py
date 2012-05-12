# -*- coding:utf-8
#!/usr/bin/env python
from Synsebot import Synsebot as Bot

if __name__ == '__main__':
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='TROLLOLOLOL' #The bot's nickname 
    IDENT='TROLLOLOLOL' 
    REALNAME='Informatikk: språk og teknologi botten.' 
    OWNER='ISK' #The bot owner's nick 
    
    bot = Bot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    #bot.join("#iskbot")
    bot.join("#iskbot")
    bot.start()
