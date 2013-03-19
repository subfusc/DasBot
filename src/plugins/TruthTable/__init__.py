# -*- coding: utf-8 -*-
from tt import Truth
import GlobalConfig as conf

MAXVARS = 3
SEPERATORSPACES = '   '

class Plugin(object):

    def __init__(self):
        self.truth = Truth()

    def stop(self):
        del(self.truth)

    def help(self, command, argc, channel, **kwargs):
        if command == 'truth':
            return [(1, kwargs['from_nick'], "!truth [logical expression]"),
                    (1, kwargs['from_nick'], "Calculates the logical expression")]

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND TruthTable") # Dunno why this is here
        if kwargs['auth_nick'] != None:
            if command == 'truth':
                parsedOutput = self.truth.parse(str(args))
                output = []

                for line in parsedOutput:
                    output.append( (0, channel, kwargs['from_nick'], line) )

                return output
