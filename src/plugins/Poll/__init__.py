# -*- coding: utf-8 -*-
# TODO:
# endpoll --fastforward og --discard
# poll --status

import GlobalConfig as conf

from Poll import PollBot
from time import sleep
import time

VOTE_REPLY_ON_SUCCESS = 0
VOTE_REPLY_ON_FAIL = 1

class Plugin(object):

    def __init__(self):
        self.p = PollBot()

    def stop(self):
        del(self.p)

    def help(self, command, argc, channel, **kwargs):
        if command == 'poll':
            return [(1, kwargs['from_nick'], conf.COMMAND_CHAR + "poll [length] [question]? alternative1, alternative2, ...")]

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
                        return [(0, channel, 'Fuck off')] #TODO: Lur tilbakemelding. Evt lage en bedre sjekk for hvor mange argumenter som må til

                    response = self.p.startPoll(kwargs['from_nick'], channel, args)

                    if response == None:
                        return [(0, channel, "Poll failed to initiate.")]

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

                    return [(0, channel, 'The poll: ' + self.p.activePoll[channel].question + ' is currently active. The current leader(s) is/are: '
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
                    kwargs['del_job'](self.p.activePoll[channel].cronId[0])
                    kwargs['del_job'](self.p.activePoll[channel].cronId[1])

                    self.p.forceEndPoll(channel)

                    return [(0, channel, 'Poll probably ended successfully.')]

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
