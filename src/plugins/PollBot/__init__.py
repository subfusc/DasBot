# -*- coding: utf-8 -*-
import GlobalConfig as conf

from Poll import PollBot
from Poll import PollErrors
from threading import Thread
from time import sleep

POLLLENGTH = 60

class Plugin(object):

    def __init__(self):
        self.p = PollBot()
        self.t

    def stop(self):
        del(self.p)

    def help(self, command, argc, channel, **kwargs):
        if command == 'poll':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + "poll [question] alternative1, alternative2, ...")]

    def interval(self, timer):
        if timer == 0:
            p = self.p.activePoll
            self.p.endPoll()



    def countdown(self):
        timer = POLLLENGTH

        while timer > 0:
            sleep(1)
            timer -= 1
            self.interval(timer)

    def startPoll(self, initiater, channel, argument):
        response = self.p.startPoll(initiater, channel, argument)

        if type(response) != int:
            self.t = Thread(target=self.countdown())
            # Return a shout about the newly started poll
            return [(0, channel, initiater, "" )]

        return [(0, channel, initiater, PollErrors.getErrorMessage(response))]

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND PollBot")
        if command == 'poll':
            if kwargs['auth_nick'] != None:
                if args != "":
                    return self.startPoll(kwargs['from_nick'], channel, args)

        if command == 'vote':
            if self.p.vote(kwargs['from_nick'], args) == None:
                pass # Skriv ut feilmelding
            else:
                pass # Skriv ut sukseemelding
