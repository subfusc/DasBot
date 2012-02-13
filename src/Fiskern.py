# -*- coding: utf-8 -*-
import AuthBot

class Fiskern(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(Fiskern, self).__init__(host, port, nick, ident, realname)

    def listen(self, command, msg, channel=None, **kwargs):
        super(Fiskern, self).listen(command, msg, channel=channel, **kwargs)
        print "RUNNING FISKERN BOT"

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Fiskern' #The bot's nickname 
    IDENT='Fiskern' 
    REALNAME='Ola Nordlenning' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = Fiskern(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "Ingenting e som å lig i fjorn å feske på en fin sommardag!")
    bot.msg("#nybrummbot", "Dæsken så mye fesk det e i fjorn i dag!")
    bot.start()
