# -*- coding: utf-8 -*- 
from GlobalConfig import *
import re

SHADAP_RE = r'[^s]*sh[ua][td][^ua]*[ua]p'

class Plugin(object):

    def __init__(self):
        self.shadap = re.compile(SHADAP_RE, re.I)
    
    def listen(self, msg, channel, **kwargs):
        if msg.find(NICK) != -1 and self.shadap.search(msg):
            return [(0, channel, kwargs['from_nick'], 'Fuck you! I\'m only doing what I\'m being told to do.')]

    def cmd(self, command, args, channel, **kwargs):
        if command == 'losers':
            return [(0, channel, kwargs['from_nick'], 'The losers in this channel are: ' + ", ".join([ u for u in kwargs['channel_users'] if not (u == NICK or u in kwargs['nick_to_user'])]))]
        if command == 'help':
            return [(1, kwargs['from_nick'], "To get help for a given command use ? instead of !."),
                    (1, kwargs['from_nick'], "To get help about help, use ? only.")]
        if command == 'say' and args != None:
            alist = args.split()
            return [(0, alist[0], " ".join(alist[1:]))]
