import sys 
import socket 
import string 

class IRCbot:

    def __init__(self, host, port, nick, ident, realname):
        self.host = host
        self.port = port
        self.nick = nick
        self.ident = ident
        self.realname = realname
        self.s = socket.socket() #Create the socket 
        self.channel = {}

    def connect(self):
        self.s.connect((self.host, self.port)) #Connect to server 
        self.s.send('NICK ' + self.nick + '\n') #Send the nick to server 
        self.s.send('USER ' + self.ident + ' ' + self.host + ' SB: ' + self.realname + '\n') #Identify to server

        while 1: # Join loop 
            line = self.s.recv(1024) #recieve server messages 
            print line #server message is output 
            line = line.rstrip() #remove trailing 'rn' 
            line = line.split() 
            
            if line[3].find(':\x01VERSION\x01') != -1: #This is Crap 
                print "Presumably connected"
                self.msg(line[0][1:], '\x01VERSION 0.0.0.0.0.0.1\x01\n')
                break;
            
            if (line[0]=='PING'): #If server pings then pong 
                print "replying to pong \'%s\'" % ('PONG ' + line[1])
                self.s.send('PONG ' + line[1] + '\n')  
        
        return True
    
    def join(self, name):
        if not name in self.channel:
            self.channel[name] = []
            self.s.send('JOIN ' + name + '\n');
            line = self.s.recv(1024)
            line = line.rstrip()
            line = line.split("353")
            if len(line) >= 2:
                line = line[1].split(":")
                nicks = line[1]
                
                nicks = nicks.split()
                for nick in nicks:
                    if nick[0] == "+" or nick[0] == "@":
                        self.channel[name].append(nick[1:])
                    else:
                        self.channel[name].append(nick)
                        
                return "I Joined " + name + ", and ready to spy on: " + ", ".join(self.channel[name])
            else:
                del self.channel[name]
                return "DID NOT JOIN! LULZ!"

        else:
            return "Allready in channel"

    def part(self, name):
        if name in self.channel:
            self.s.send('PART ' + name + '\n')
            del self.channel[name]
            return "PULLING OUUUUTTT!"
        else:
            return "Not in that channel"

    def msg(self, name, message, to = None):
        if to:
            self.s.send("PRIVMSG " + name + " :" + to + ", " + message + "\n")
        else:
            self.s.send("PRIVMSG " + name + " :" + message + "\n")
        
    def notify(self, name, message):
        self.s.send("NOTICE " + name + " :" + message + "\n")

    def start(self):
        while 1: # Main Loop
            line = self.s.recv(1024) #recieve server messages
            line = line.rstrip()

            print line #server message is output             
            line = line.split()
            
            if line[0] == 'PING': #If server pings then pong 
                print "replying to pong \'%s\'" % ('PONG ' + line[1])
                self.s.send('PONG ' + line[1] + '\n')
                
            if line[1] == 'PRIVMSG': #Call a parsing function 
                self.parsemsg(line)

            if line[1] == 'QUIT':
                self.quit(line)
            
            self.listen(line)

    def listen(self, line): pass

    def parsemsg(self, line):
        nick, domain = line[0].split("!")
        nick = nick[1:]
        message = " ".join(line[3:])
        message = message[1:]

        if line[2] == self.nick:
            self.private_message(nick, domain, message)
        else:
            self.channel_message(line[2], nick, domain, message)

    def channel_message(self, channel, nick, domain,  message):
        print "Channel Message from %s@%s" % (nick, domain)

    def private_message(self, nick, domain, message):
        print "Private Message from %s@%s" % (nick, domain)

    def quit(self,line):
        print "somone quit"

if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Botty' #The bot's nickname 
    IDENT='botty' 
    REALNAME='Aweseome Bot' 
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = IRCbot(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.notify("#nybrummbot", "HAI PEEPS!")
    bot.start()
