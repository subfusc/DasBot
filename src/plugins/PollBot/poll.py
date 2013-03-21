# -*- coding: utf-8 -*-

# TODO
# Make error messages

class Poll(object):

    def __init__(self, initiater, channel, question, alternatives):
        self.question = question
        self.alternatives = alternatives

        self.initiater = initiater

        self.voters = [ ]

        self.channel = channel

class PollBot(object):

    def __init__(self):
        self.activePoll = None
        self.keywords = ['or', 'eller']

    def listToDictionary(self, l):
        returnValue = { }

        for item in l:
            returnValue[item] = 0

        return returnValue

    def getAlternatives(self, argument):

        returnValue = argument.replace(" ","")

        for word in self.keywords:
            if word in argument:

                if returnValue[-1] == '?':
                    returnValue = returnValue[:-1]

                return self.listToDictionary(returnValue.split(word))

        if '?' not in argument:
            return None

        returnValue = self.listToDictionary(returnValue[returnValue.index('?')+1:].split(','))

        return returnValue

    def startPoll(self, initiater, channel, argument):

        alternatives = self.getAlternatives(argument)

        if alternatives == None:
            return None

        question = self.getQuestion(argument)

        if question == None:
            return None

        self.activePoll = Poll(initiater, channel, question, alternatives)

    def endPoll(self):
        # Legg til endt poll og resultater i db?
        self.activePoll = None

    def vote(self, voter, alternative):
        if self.activePoll == None:
            return None

        if voter in self.activePoll.voters:
            return None

        if alternative not in self.activePoll.alternatives:
            return None

        self.activePoll.voters.append(voter)
        self.activePoll.alternatives[alternative] += 1

class PollErrors():
    @staticmethod
    def getErrorMessage(error):
        pass

p = PollBot()
