# -*- coding: utf-8 -*-
from GlobalConfig import *

import Karma
import IRCbot

class KarmaBot(IRCbot.IRCbot):

        def __init__(self, host, port, nick, ident, realname):
                super(KarmaBot, self).__init__(host, port, nick, ident, realname)
                self.k = Karma.Karma()


        def cmd(self, command, args, channel, **kwargs):
                super(KarmaBot, self).cmd(command, args, channel, **kwargs)
                if VERBOSE: print("COMMAND KarmaBot")
                print(command)
                if command == '+1' and len(args.split()) == 1: # TODO: Check if args really is a user
                        to = args.strip()
			
                        if kwargs['from_nick'] == to:
                                self.k.delKarma("ISKBot", kwargs['from_nick'])
                                self.msg(channel, "What goes around comes around. -1 for trying to +1 yourself. :)")
                                return

			if not self.isUser(channel, to):
				self.msg(channel, to + " is not a user.")
				return

                        self.k.addKarma(kwargs['from_nick'], to)
                        self.msg(channel, to + " just got a +1. Way to go ;)")
			return
                elif command == '-1' and len(args.split()) == 1:
                        to = args.strip()
			
                        if kwargs['from_nick'] == to:
                                self.msg(channel, "Trying to win a bad karma contest? Sorry to burst your bubble. No voting on yourself either way.")
                                return

			if not self.isUser(channel, to):
				self.msg(channel, to + " is not a user.")
				return

                        self.k.delKarma(kwargs['from_nick'], to)
                        self.msg(channel, to + " just got a -1. Get a grip, " + to + ".")
			return

                elif command == 'topkarma':
                        if args and len(args.split()) == 1:
                                try:
                                        args = int(args[0])
                                except:
                                        return
                                result = self.k.getTopUsers(args)

                                if args > 3:
                                        rank = 1
                                        self.msg(kwargs['from_nick'], "Karma top:")
                                        for user in result:
                                                self.msg(kwargs['from_nick'], "#" + str(rank) + " <" + user[0] + "> with " + str(user[1]) + " karma")
                                                rank += 1
                                                return
                                elif args <= 3:
                                        rank = 1
                                        output = "The karma top: "
                                        for user in result:
                                                output += "#" + str(rank) + " <" + user[0] + "> with " + str(user[1]) + " karma || "
                                                rank += 1

                                        self.msg(channel, output[:-3])
					return
		elif command == '+u':
			self.msg(channel, str(self.isUser(channel, kwargs['from_nick'])))
			return
                elif command == 'topkarma' and not args:
                	rank = 1
                	output = "The karma top: "
                        result = self.k.getTopUsers(3)
                        for user in result:
                        	output += "#" + str(rank) + " <" + user[0] + "> with " + str(user[1]) + " karma || "
                                rank += 1
			
                        self.msg(channel, output[:-3])
			return

	def isUser(self, channel, username):
		users = []
		for ulist in self.channel[channel].values():
			users.extend(ulist)
		
		if username in users:
			return True
		else:
			return False
				

if __name__ == '__main__':
	HOST = 'irc.ifi.uio.no'
	PORT = 6667
	NICK = 'Eeyore'
	IDENT = 'Eeyore'
	REALNAME = 'Lonely donkey Eeyore'
	OWNER = 'kripede'

	bot = KarmaBot(HOST, PORT, NICK, IDENT, REALNAME)
	bot.connect()
	bot.join('#eeyore')
	bot.start()
