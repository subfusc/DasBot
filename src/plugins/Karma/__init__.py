# -*- coding: utf-8 -*-
from Karma import Karma
import GlobalConfig as conf

class Plugin(object):

    def __init__(self): 
        self.k = Karma()

    def stop(self):
        del(self.k)

    def help(self, command, argc, channel, **kwargs):
        if command == 'karma':
            return [(1, kwargs['from_nick'], "!karma [top]"),
                    (1, kwargs['from_nick'], "Shows your karma or the top karma users. Use !+1 <nick>"),
                    (1, kwargs['from_nick'], "!-1 <nick> to give a user karma. The user has to have an account"),
                    (1, kwargs['from_nick'], "in the bots system to give/receive karma. See '?register'")]
        
    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND KarmaBot")
        if kwargs['auth_nick'] != None:
            if command == '+1':
                to = args.strip()
                if kwargs['from_nick'] == to:
                    self.k.delKarma(kwargs['auth_nick'])
                    return [(0, channel, kwargs['from_nick'], "What goes around comes around. -1 for trying to +1 yourself. :)")]

                if not to in kwargs['nick_to_user']:
                    return [(0, channel, kwargs['from_nick'], to + " is not logged in as a user.")]

                self.k.addKarma(kwargs['nick_to_user'][to])
                return [(0, channel, to + " just got a +1. Way to go ;)")]

            elif command == '-1':
                to = args.strip()
                if kwargs['from_nick'] == to:
                    return [(0, channel, kwargs['from_nick'], "Trying to win a bad karma contest? Sorry to burst your bubble. No voting on yourself either way.")]

                if not to in kwargs['nick_to_user']:
                    return [(0, channel, to + " is not logged in as a user.")]

                self.k.delKarma(kwargs['nick_to_user'][to])
                return [(0, channel, to + " just got a -1. Get a grip, " + to + ".")]
            
            elif command == 'karma':
                if not args:
                    cmd = []
                else:
                    cmd = args.split()
                    
                if len(cmd) == 0 and kwargs['from_nick'] in kwargs['nick_to_user']:
                    karma = self.k.getUserKarma(kwargs['nick_to_user'][kwargs['from_nick']])

                    if karma:
                        return [(1, kwargs['from_nick'], "You have " + str(karma) + " karma.")]
                    else:
                        return [(1, kwargs['from_nick'], "You aren't logged in as a user with karma. :(")]

                elif len(cmd) == 1:
                    if cmd[0].strip() == 'top':
                        result = self.k.getTopUsers(3) # Number of users to show
                        rank = 1
                        output = "The karma top3 is: "
                        
                        for user in result:
                            if user[0] in kwargs['user_to_nick']:
                                output += "#" + str(rank) + " <" + kwargs['user_to_nick'][user[0]] +\
                                  "> with " + str(user[1]) + " karma || "
                                rank += 1
                            else:
                                output += "#" + str(rank) + " <" + user[0] +\
                                  "> with " + str(user[1]) + " karma || "
                                rank += 1

                        return [(0, channel, output[:-3])]
                    else:
                        karma = self.k.getUserKarma(cmd[0])
                        if karma:
                            return [(0, channel, kwargs['from_nick'], cmd[0] + " has " + str(karma) + " karma.")]
                        else:
                            return [(1, kwargs['from_nick'], "This user doesn't exist in the database.")]
				
