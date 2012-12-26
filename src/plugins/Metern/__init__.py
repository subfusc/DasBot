# -*- coding:utf-8 -*-
import os
import re
import GlobalConfig as conf

class Plugin(object):

    def cmd(self, command, args, channel, **kwargs):
        if conf.DEBUG: print "COMMAND Meteren!"
        if command == 'metern':
            return [(0, channel, kwargs['from_nick'], self.metern())]

    def metern(self):
        response = os.popen('rwho').readlines()
        maskiner = re.compile('sorterytter|spartiate|regent|reigersber|soleil|speedwell|quittance|ramilles|starrenburg|slesvig|repulse|skjold|spes|stcroix|vengance|sejer')
        pattern = re.compile('.::0.')
        response = [line.split(" ")[0] for line in response if pattern.search(line) and maskiner.search(line)]
        return "Disse er på metern nå: " + ", ".join(response)
