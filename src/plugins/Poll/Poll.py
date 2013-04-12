# -*- coding: utf-8 -*-

import os
import re
import time
import urllib
import urllib2

import GlobalConfig as conf

# TODO
# Make error messages
# Numerate alternatives
# Unicode, case sensitive symbols in .vote alternatives

POLL_LENGTH = 60 * 5                        # Poll default length in seconds
POLL_HISTORY = True                         # Enable/disable poll history
RESULT_FILE = r'data/pollresults'           # Poll history data location
VOTE_LOCK = False                           # 'Locks' a vote. One can't change the vote after its been set

TIME_VALUE = { 'd':86400,
        'h':3600,
        'm':60,
        's':1}

class Poll(object):

    def __init__(self, initiater, channel, question, alternatives, length):
        self.question = question
        self.alternatives = alternatives
        self.winner = [ "", 0 ]
        self.length = length
        self.initiated = time.time()

        self.initiater = initiater

        self.voters = { }

        self.channel = channel
        self.cronId = ()

class PollBot(object):

    def __init__(self):
        self.activePoll = { }
        self.keywords = ['or', 'eller', 'vs']
        self.pollLength = POLL_LENGTH
        self.POLL_HISTORY = POLL_HISTORY
        self.timeRe = re.compile('(?P<days>\dd(ays?)?)?(?P<hours>\d{1,2}h(ours?)?)?(?P<minutes>\d{1,2}m(inutes?)?)?(?P<seconds>\d{1,2}s(econds?)?)?')
        self.altRe = re.compile('[,\s?\w+,]')

    def getAlternatives(self, argument):

        words = argument.split(' ')

        if words[1] in self.keywords and len(words) == 3:
            if words[2][-1] == '?':
                words[2] = words[2][:-1]

            return { words[0]:0, words[2]:0 }

        if '?' not in argument:
            return None

        words = argument.split('?')[1]
        words = words.split(',')

        alternatives = { }

        for alt in words:
            if alt != '':
                alt = alt.strip()
                if alt[0] != ',':
                    alt = ',' + alt
                if alt[-1] != ',':
                    alt = alt + ','
                if self.altRe.search(alt) == None:
                    return None
                alternatives[alt[1:-1]] = 0

        if len(alternatives) < 2:
            return None

        return alternatives

    def getQuestion(self, argument):

        if '?' not in argument:
            return argument

        return argument[:argument.index('?')+1]

    def getLeader(self, channel):

        if channel not in self.activePoll:
            return None

        votes = []

        for item in self.activePoll[channel].alternatives:
            votes.append([self.activePoll[channel].alternatives[item], item])

        votes = sorted(votes, reverse=True)

        result = [ votes[0][0], []]

        for item in votes:
            if item[0] == result[0]:
                result[1].append(item[1])
            else:
                break

        return result

    def startPoll(self, initiater, channel, argument):

        if channel in self.activePoll:
            self.pollDebug('Channel is in self.activePoll')
            return 1

        search = self.timeRe.search(argument)

        searchValid = False
        if search != None:
            for item in search.groups():
                if item != None:
                    argument = argument.split(' ', 1)[1]
                    searchValid = True
                    break

        alternatives = self.getAlternatives(argument)

        if alternatives == None:
            self.pollDebug('No alternatives found')
            return 2

        question = self.getQuestion(argument)

        if question == None:
            self.pollDebug('No question found')
            return 3

        time = 0

        if searchValid:

            if search.group('days'):
                time += int(search.group('days')[:-1]) * TIME_VALUE['d']
            if search.group('hours'):
                time += int(search.group('hours')[:-1]) * TIME_VALUE['h']
            if search.group('minutes'):
                time += int(search.group('minutes')[:-1]) * TIME_VALUE['m']
            if search.group('seconds'):
                time += int(search.group('seconds')[:-1])

            if time > 2 * TIME_VALUE['d'] or time < 10:
                return 4
        else:
            time = self.pollLength

        self.activePoll[channel] = Poll(initiater, channel, question, alternatives, time)

        return 0

    def endPoll(self, channel):

        if channel not in self.activePoll:
            return None

        if POLL_HISTORY:
            f = open(RESULT_FILE, 'a')

            f.write(self.activePoll[channel].question + ';' + self.activePoll[channel].winner[0] + ':' + str(self.activePoll[channel].winner[1]) + '\n')
            f.flush()
            f.close()

        del(self.activePoll[channel])

    def forceEndPoll(self, channel):
        del(self.activePoll[channel])

    def vote(self, channel, voter, alternative):

        if channel not in self.activePoll:
            self.pollDebug('channel is not in self.activePoll')
            return None

        alternative = alternative.lower().strip()

        for alt in self.activePoll[channel].alternatives:
            if alternative == alt.lower():
                if voter in self.activePoll[channel].voters:
                    if VOTE_LOCK:
                        return None
                    self.removeVote(channel, voter)

                self.activePoll[channel].voters[voter] = alt
                self.activePoll[channel].alternatives[alt] += 1
                return 1

        self.pollDebug('alternative ' + alternative + ' is not in self.activePoll[channel].alternatives')
        return None

    def removeVote(self, channel, voter):

        if channel not in self.activePoll:
            return None

        if voter not in self.activePoll[channel].voters:
            return None

        self.activePoll[channel].alternatives[self.activePoll[channel].voters[voter]] -= 1

        del(self.activePoll[channel].voters[voter])

    def printPollHistory(self):
        url = 'http://pastebin.com/api/api_post.php'

        try:
            f = open(RESULT_FILE)
        except:
            return None

        code = ''

        for line in f:
            line = line.split(';')
            line[1] = line[1].split(':')

            code += 'Question: "' + line[0] + '" with the winning answer: ' + line[1][0] + ' by ' + line[1][1][:-1] + ' votes.\n'

        values = { 'api_option':'paste',
                'api_paste_private':'1',
                'api_paste_name':'Pollbot history',
                'api_paste_expire_date':'10M',
                'api_dev_key':'4c59086bba061d1c49277a824599343c',
                'api_paste_code':code }

        data = urllib.urlencode(values)
        request = urllib2.Request(url, data)
        response = urllib2.urlopen(request)
        return(response.read())

    def delPollHistory(self):
        try:
            with open(RESULT_FILE): pass

            os.remove(RESULT_FILE)
        except:
            return None

    def pollDebug(self, msg):
        if conf.DEBUG:
            print(msg)
