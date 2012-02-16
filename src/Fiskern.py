# -*- coding: utf-8 -*-
import AuthBot
import time
from GlobalConfig import *
from IRCFonts import *
import re, sys, math
numbers = r'(\d*\.\d+|\d+)'
twonroper = r'' + numbers + '\s?([^.])\s?' + numbers + ''
onenroper = r'^(\D*)\s' + numbers + '$'
command = r'/.*'

class Fiskern(AuthBot.AuthBot):
        
    def __init__(self, host, port, nick, ident, realname):
        super(Fiskern, self).__init__(host, port, nick, ident, realname)

    def cmd(self, command, args, channel, **kwargs):
        super(Fiskern, self).cmd(command, args, channel, **kwargs)        

        if command == "insult":
            self.msg(channel, "e du fette sprø i haue? æ ork da faen ikkje å ta mæ ti tel å lag sånnhærre tullekommandoa!", to=kwargs["from_nick"])
        elif command == "tell":
            self.private_msg(kwargs["from_nick"], "emanuel is lazy")
        elif command == "whos":
            self.msg(channel, str(self.channel[channel][args]) if args in self.channel[channel] else "Not legal key", to=kwargs['from_nick'])
        elif command == "notifyall":
            output = ""
            for key in self.channel[channel]:
                for user in self.channel[channel][key]:
                    output += user + " "
            self.msg(channel, output)
            self.msg(channel, "se tell hælvette å føll me hær!")
        elif command == "calc":
            result = self._math(args)
            if result: self.msg(channel, result, to=kwargs["from_nick"])
            else: self.msg(channel, result, to=kwargs["from_nick"])

        elif command == "topic":
            if args:
                self.topic(channel, args)
            else:
                self.topic(channel, "Der hammermäßige IRC Bot der Computerlinguisten")

        elif command == "nick":
            self.nick(args)

        elif command == "ban":
            args = args.split()
            self.ban(channel, nick=args[0], ident=args[1], hostmask=args[2])

        elif command == "unban":
            args = args.split()
            self.unban(channel, nick=args[0], ident=args[1], hostmask=args[2])
            
        elif command == "kick":
            print "'%s''%s''%s'" % (channel, args, command)
            self.kick(channel, args)

        elif command == "here":
            self.msg(channel, str(self.user_in_channel(channel, args)), to=kwargs["from_nick"])
        elif command == "windows":
            self.msg(channel, "The best way to speed up your windows computer is 9.8m/s^2", to=kwargs["from_nick"])
            
    def listen(self, command, msg, channel, **kwargs):
        super(Fiskern, self).listen(command, msg, channel, **kwargs)
        if kwargs['from_nick'] == 'emanuel':
            self.msg(channel, "bipeti bapeti!", to="emanuel")
        if msg.find("!insult") != -1:
            self.msg(channel, "please !insult %s back" % (kwargs["from_nick"]))

    def management_cmd(self, command, args, **kwargs):
        super(Fiskern, self).management_cmd(command, args, **kwargs)
        if command == '482':
            self.msg(args.split()[1], "I'm not allowed to do that")
            
    def _math(self, input):
        match = re.search(twonroper, input)
        if match:
            if "." in match.group(1): num1 = float(match.group(1))
            else: num1 = int(match.group(1))
            if "." in match.group(3): num2 = float(match.group(3))
            else: num2 = int(match.group(3))

            if match.group(2) == '+': return ("Result: %g") % (num1 + num2)
            elif match.group(2) == '-': return ("Result: %g") % (num1 - num2)
            elif match.group(2) == '/': return ("Result: %g") % (num1 / float(num2))
            elif match.group(2) == '*': return ("Result: %g") % (num1 * num2)
            else: print ("Operasjonen \"%s\" er ikke funnet.") % (match.group(2))

        match = re.search(onenroper, input)
        if match:
            if "." in match.group(2): num1 = float(match.group(2))
            else: num1 = int(match.group(2))

            return "%s av %g er %g" % (match.group(1), num1, eval("math.%s(%d)" % (match.group(1), num1)))
        return None
        
if __name__ == "__main__":
    HOST='irc.ifi.uio.no' #The server we want to connect to 
    PORT=6667 #The connection port which is usually 6667 
    NICK='Fiskern' #The bot's nickname 
    IDENT='Fiskern' #The bot's identity
    REALNAME='Ola Nordlenning' #REAL NAME, sort of.
    OWNER='Subfusc' #The bot owner's nick 
    
    bot = Fiskern(HOST, PORT, NICK, IDENT, REALNAME)
    bot.connect()
    bot.join("#nybrummbot")
    bot.msg("#nybrummbot", "%s e som å lig i fjorn %s på en %s!"% (bold("Ingenting"), reverse("å fesk"), underline("fin sommardag")))
    #bot.msg("#nybrummbot", "Dæsken så mye fesk det e i fjorn i dag!")
    bot.notify("Subfusc", "hør du ette eller?")
    bot.start()
