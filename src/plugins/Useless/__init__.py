# -*- coding: utf-8 -*- 
from GlobalConfig import *
import re
from random import randint

SHADAP_RE = r'[^s]*sh[ua][td][^ua]*[ua]p'
DICE_CMD_RE = r'^(?P<number>[0-5]?\d?)[dD](?P<size>[1-9]|\d{2,3})$'
UNIVERSE_RE = r'^.*natur.*univers'

class Plugin(object):

    def __init__(self):
        self.shadap = re.compile(SHADAP_RE, re.I)
        self.dicere = re.compile(DICE_CMD_RE, re.U)
        self.universe = re.compile(UNIVERSE_RE, re.I)
        
    def listen(self, msg, channel, **kwargs):
        if msg.find(NICK) != -1 and self.shadap.search(msg):
            return [(0, channel, kwargs['from_nick'], 'Fuck you! I\'m only doing what I\'m being told to do.')]

        if msg.find(NICK) != -1 and self.universe.search(msg):
            return [(0, channel, kwargs['from_nick'], 'The universe is a spheroid region, 705 meters in diameter.')]

    def cmd(self, command, args, channel, **kwargs):
        if command == 'losers':
            return [(0, channel, kwargs['from_nick'], 'The losers in this channel are: ' + ", ".join([ u for u in kwargs['channel_users'] if not (u == NICK or u in kwargs['nick_to_user'])]))]
        if command == 'help':
            return [(1, kwargs['from_nick'], "To get help for a given command use ? instead of !."),
                    (1, kwargs['from_nick'], "To get help about help, use ? only.")]
        if command == 'say' and args != None:
            alist = args.split()
            return [(0, alist[0], " ".join(alist[1:]))]
        match = self.dicere.match(command)
        if command == 'coin' or command == 'toss' or command == 'cointoss':
            if randint(1, 2) == 1:
                return [(0, channel, kwargs['from_nick'], "Head")]
            else:
                return [(0, channel, kwargs['from_nick'], "Tail")]
        if match:
            if match.group('number') != '':
                answ = [randint(1, int(match.group('size'))) for x in range(0, int(match.group('number')))]
                answ = "Sum: {s}, {l}".format(s = sum(answ), l = answ)
            else:
                answ = randint(1, int(match.group('size')))
                if match.group('size') == '20' and answ == 20:
                    answ = 'CRITICAL HIT!'
            return [(0, channel, kwargs['from_nick'], str(answ))]

if __name__ == '__main__':
    print('done')
    p = Plugin()
    print(p.cmd('2d6', None, '#iskbot'))
