import IRCbot

class AuthBot(IRCbot.IRCbot):
    """
    This is a class where the IRCBot has an authentication system
    TODO: Use existing authentication mekanism
    """

    def __init__(self, host, port, nick, ident, realname):
        super(AuthBot, self).__init__(host, port, nick, ident, realname)

    def listen(self, line):
        super(AuthBot, self).listen(line)
        print "RUNNING AUTH BOT"

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Subot' #The bot's nickname 
    IDENT='Subot' 
    REALNAME='Aweseome Bot' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = AuthBot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "HAI PEEPS!")
    bot.msg("#nybrummbot", "emanuel: Example for you bro!")
    bot.start()
