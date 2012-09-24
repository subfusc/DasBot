# -*- coding: utf-8 -*-
from Kafe import Kafe
#from GlobalConfig import *

class Plugin(object):

    def __init__(self):
        self.middag = Kafe('inf')
        
    def cmd(self, command, args, channel, **kwargs):
        if command == 'middag':
            middager = None
            if args != None: 
                args = args.lower()
                if args.find(' ') != -1:
                    args = args.split()
                    if args[0] == '-f':
                        args = ' '.join(args[1:])
                        middager = self.middag.todaysDinner(args, False)
                    else:
                        args = ' '.join(args)
                        middager = self.middag.todaysDinner(args)
                elif args == '-f':
                    middager = self.middag.todaysDinner(None, check_closing=False)
                    args = self.middag.cafename
                else:
                    middager = self.middag.todaysDinner(args)
            else:
                middager = self.middag.todaysDinner(None)
                args = self.middag.cafename

            middager = (middager[0].encode('utf-8'), middager[1])
            if middager[1] == None: return [(0, channel, 'Sorry, jeg kjenner ikke til {k}'.format(k=middager[0]))]
            if middager[1] == 'Stengt': return [(0, channel, '{k} er stengt'.format(k=middager[0]))]
            
            rarr = [(0, channel, "Dagens meny på {f}".format(f = middager[0]))]

            for t, middag in middager[1]:
                middag = middag.encode('utf-8')
                t = t.encode('utf-8')
                #print("in loop: {r}{m}".format(m = rett[1], r = chardet.detect(rett[0])))
                rarr.append((0, channel, t + ": " + middag))
            return rarr
