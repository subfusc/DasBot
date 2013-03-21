# -*- coding: utf-8 -*-
from tt import Truth
import GlobalConfig as conf

class Plugin(object):

    def __init__(self):
        self.truth = Truth()

    def stop(self):
        del(self.truth)

    def help(self, command, argc, channel, **kwargs):
        if command == 'tt':
            return [(1, kwargs['from_nick'], "!tt [logical expression]"),
                    (1, kwargs['from_nick'], "Calculates the logical expression and returns a 'truth table'"),
                    (1, kwargs['from_nick'], "containing the results."),
                    (1, kwargs['from_nick'], "Remember:"),
                    (1, kwargs['from_nick'], "Paranthesises must be symmetrical. For each '(', there must be a ')'."),
                    (1, kwargs['from_nick'], "We have a limit of " + str(self.truth.truth.maxvars) + " variables. This because the table will expand"),
                    (1, kwargs['from_nick'], "by 2^nvars which can result in alot of calculation.")]

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND TruthTable")
        if command == 'tt':
            parsedOutput = self.truth.parse(str(args))

            if type(parsedOutput) == int:
                return [(0, channel, kwargs['from_nick'], self.truth.getError(parsedOutput) + ' For help, type ' + conf.HELP_CHAR + 'tt')]

            output = []

            for line in parsedOutput:
                output.append( (0, channel, kwargs['from_nick'], line) )

            return output
