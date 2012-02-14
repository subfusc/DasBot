import os
import sys
import AuthBot
import insult
import nltk
import log_stats
from GlobalConfig import *

class botmod(AuthBot.AuthBot):
      def __init__(self, host, port, nick, ident, realname):
        super(botmod, self).__init__(host, port, nick, ident, realname)

      def cmd(self, command, args, channel, **kwargs):
        super(botmod, self).cmd(command, args, channel, **kwargs)
        if VERBOSE: print "COMMAND AUTHBOT!"
        if command == 'insult':
          if args:
            self.msg(channel, insult.insult(args))
          else:
            self.msg(channel, insult(kwargs['from_nick']))

        if command == 'count':
          if args:
            self.msg(channel, log_stats.msg_rank(args.split()[0]))
          else:
            self.msg(channel, 'Globals:')
            globs = log_stats.globals()
            for a, b in reversed(globs):
              self.msg(channel, a + ' - ' + str(b))
    
      def listen(self, command, msg, channel, **kwargs):
        super(botmod, self).listen(command, msg, channel, **kwargs)
        if VERBOSE: print "LISTEN AUTHBOT!"
        if kwargs['from_nick'] != 'ifidm':
            os.system('echo ' + kwargs['from_nick'] + ':::::' + msg + ' >> log')
        
if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='botbotbot' #The bot's nickname 
    IDENT='itsame' 
    REALNAME='itsame' 
    OWNER='eman' #The bot owner's nick 
    chan = sys.argv[1]
    
    bot = botmod(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join(chan)
    #bot.notify(chan, "HAI PEEPS!")
    #bot.msg(chan, "Example for you bro!", to="emanuel")
    bot.start()