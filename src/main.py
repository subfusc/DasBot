# -*- coding:utf-8
#!/usr/bin/env python
from AuthBot import AuthBot as Bot

if __name__ == '__main__':
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Subot' #The bot's nickname 
    IDENT='Subot' 
    REALNAME='Aweseome Bot' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = Bot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "HAI PEEPS!")
    bot.msg("#nybrummbot", "Example for you bro!", to="emanuel")
    bot.start()
