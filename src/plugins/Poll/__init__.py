# -*- coding: utf-8 -*-
# TODO:

import GlobalConfig as conf
from Poll import PollBot

import math
import time
from time import sleep

VOTE_REPLY_ON_SUCCESS = 0
VOTE_REPLY_ON_FAIL = 1

class Plugin(object):

    def __init__(self):
        self.p = PollBot()

    def stop(self):
        del(self.p)

    def help(self, command, argc, channel, **kwargs):
        if command == 'all':
            return [(1, kwargs['from_nick'], 'PollBot: poll, vote, endpoll, pollhistory')]
        if command == 'poll':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + "poll [length] question? [alternative1, alternative2, ...]"),
                    (1, kwargs['from_nick'], 'where [length] is n[d|h|m|s]. n is amount, d is days, h is hours, m is minutes and s is seconds.'),
                    (1, kwargs['from_nick'], 'Initiates a new poll. Leave empty during a poll to see poll status.')]
        if command == 'vote':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + 'vote [alternative]'),
                    (1, kwargs['from_nick'], 'Vote for an alternative. Leave empty to see the available alternatives.')]
        if command == 'pollhistory':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + 'pollhistory [--delete]'),
                    (1, kwargs['from_nick'], 'Displays the poll history. If --delete option is specified, the poll history gets deleted.')]
        if command == 'endpoll':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + 'endpoll [--kill]'),
                    (1, kwargs['from_nick'], 'Ends a poll. If --kill option is specified, the poll gets killed and no results are shown.')]

    def getError(self, code):
        if code == 1:
            return 'Already a poll active.'
        elif code == 2:
            return 'No alternatives found.'
        elif code == 3:
            return 'No question found.'
        elif code == 4:
            return 'The poll must be set to less than 2 days and more than 0 sec into the future when using time.'

    def halfway(self, channel):
        return [(0, channel, 'The poll: "' + self.p.activePoll[channel].question + '" is half way done. Hurry up and vote.')]

    def countdown(self, channel):

        winnerdata = self.p.getLeader(channel)

        self.p.activePoll[channel].winner[1] = str(winnerdata[0])

        winners = ''

        if len(winnerdata[1]) > 1:
            result = 'In the poll "' + self.p.activePoll[channel].question + '" the winner is tied between '

            for item in winnerdata[1]:
                winners += item + ", "

            winners = winners[:-2]

            result += winners

            result += ' with ' + str(winnerdata[0]) + ' vote(s).'
        else:
            winners = winnerdata[1][0]
            result = 'In the poll "' + self.p.activePoll[channel].question + '" the winner is: ' + winners + ' with ' + str(winnerdata[0]) + ' vote(s).'

        self.p.activePoll[channel].winner[0] = winners
        self.p.endPoll(channel)

        return [(0, channel, result)]

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print("COMMAND PollBot")
        if command == 'poll':
            if args != None:
                if kwargs['auth_nick'] != None:
                    if len(args.strip().split()) < 3:
                        return None #TODO: Lur tilbakemelding. Evt lage en bedre sjekk for hvor mange argumenter som må til

                    response = self.p.startPoll(kwargs['from_nick'], channel, args)

                    if response > 0:
                        return [(0, channel, self.getError(response))]

                    # TODO:
                    # Fjerne dette. En ryddigere måte å debugge parsing
                    #self.p.endPoll(channel)
                    #return [(0, channel, "Parse ok")]

                    self.p.activePoll[channel].cronId = [ kwargs['new_job']((time.time() + int(self.p.activePoll[channel].length/2), self.halfway, [channel]))
                                                         ,kwargs['new_job']((time.time() + self.p.activePoll[channel].length, self.countdown, [channel])) ]

                    return [(0, channel, 'The poll: "' + self.p.activePoll[channel].question + '" has been initiated by ' + kwargs['from_nick'] +'.')]

            else:
                if channel in self.p.activePoll:

                    leaderdata = self.p.getLeader(channel)

                    leaders = ''

                    for item in leaderdata[1]:
                        leaders += item + ', '

                    leaders = leaders[:-2]

                    timeleft = time.time() - self.p.activePoll[channel].initiated # How much time has passed
                    timeleft = self.p.activePoll[channel].length - timeleft       # Length of poll minus time that has passed

                    days = timeleft / 86400
                    timeleft -= (86400 * math.floor(days))

                    hours = timeleft / 3600
                    timeleft -= (3600 * math.floor(hours))

                    mins = timeleft / 60
                    timeleft -= (60 * math.floor(mins))

                    sec = timeleft

                    timeString = ''

                    if days >= 1:
                        timeString += str(int(days)) + ' days, '
                    if hours >= 1:
                        timeString += str(int(hours)) + ' hours, '
                    if mins >= 1:
                        timeString += str(int(mins)) + ' mins, '
                    if sec >= 1:
                        timeString += str(int(sec)) + ' secs'

                    return [(0, channel, 'The poll: ' + self.p.activePoll[channel].question + ' is currently active with ' + timeString + ' left. The current leader(s) is/are: '
                        + leaders + ' with ' + str(leaderdata[0]) + ' points. Type "' + conf.COMMAND_CHAR + 'vote" for alternatives.')]
                else:
                    return [(0, channel, 'There is currently no active poll.')]

        if command == 'vote':
            if channel in self.p.activePoll:
                if args != None:
                    if self.p.vote(channel, "{i}@{h}".format(i = kwargs['from_ident'], h = kwargs['from_host_mask']), args) == 1:
                        if VOTE_REPLY_ON_SUCCESS == 1:
                            return [(0, channel, 'Vote "' + args + '" registered from ' + kwargs['from_nick'])]
                    else:
                        if VOTE_REPLY_ON_FAIL == 1:
                            return [(0, channel, 'Vote "' + args + '" failed.')]
                else:
                    output = "The alternatives are: "

                    for alt in self.p.activePoll[channel].alternatives:
                        output += alt + ", "

                    output = output[:-2] + "."
                    return [(0, channel, output)]
            else:
                return [(0, channel, 'There is currently no active poll.')]

        if command == 'endpoll':
            if kwargs['auth_nick'] != None:
                if channel in self.p.activePoll:
                    if args == '--kill':
                        kwargs['del_job'](self.p.activePoll[channel].cronId[0])
                        kwargs['del_job'](self.p.activePoll[channel].cronId[1])

                        self.p.forceEndPoll(channel)

                        return [(0, channel, 'Poll probably ended successfully.')]
                    else:
                        kwargs['del_job'](self.p.activePoll[channel].cronId[0])
                        kwargs['del_job'](self.p.activePoll[channel].cronId[1])

                        return self.countdown(channel)

                return [(0, channel, 'There is currently no active poll.')]

        if command == 'pollhistory':
            if self.p.POLL_HISTORY:
                if args == '--delete' and kwargs['auth_nick'] != None:
                    self.p.delPollHistory()
                    return [(0, channel, 'Poll history probably successfuly deleted.')]

                response = self.p.printPollHistory()
                if response == None:
                    return [(0, channel, 'No poll history could be found.')]

                return [(0, channel, 'The poll history can be found at: ' + response)]
