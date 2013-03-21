# -*- coding: utf-8 -*-
from tt import Truth
import GlobalConfig as conf

MAX_LINES_TO_CHANNEL = 5

class Plugin(object):

    def __init__(self):
        self.truth = Truth()

    def stop(self):
        del(self.truth)

    def help(self, command, argc, channel, **kwargs):
        if command == 'tt':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + "tt [logical expression]"),
                    (1, kwargs['from_nick'], "Example: .tt ((A + B) > C)"),
                    (1, kwargs['from_nick'], "Calculates the logical expression and returns a 'truth table' containing the results."),
                    (1, kwargs['from_nick'], "We have a limit of " + str(self.truth.truth.maxvars) + " variables.")]

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND TruthTable")
        if command == 'tt':
            parsedOutput = self.truth.parse(str(args))

            if type(parsedOutput) == int:
                return [(0, channel, kwargs['from_nick'], self.truth.getError(parsedOutput) + ' For help, type ' + conf.HELP_CHAR + 'tt')]

            output = []
            destination = 0

            if len(parsedOutput) > MAX_LINES_TO_CHANNEL: # Bytt til hvor mange linjer skal få lov til å gå i channel
                for line in parsedOutput:
                    output.append( (1, kwargs['from_nick'], line) )
            else:
                for line in parsedOutput:
                    output.append( (0, channel, kwargs['from_nick'], line) )

            return output
