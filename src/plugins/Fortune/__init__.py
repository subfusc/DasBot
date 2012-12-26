# -*- coding: utf-8 -*- 
# 
# Copyright (C) 2012 Herman Torjussen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://gnu.org/licenses/>.


from random import randint

MAXLINEWIDTH = 79

class Plugin(object):

    def cmd(self, command, args, channel, **kwargs):
        if command == "fortune":
            return [(0, channel, self.fortune())]
    
    def help(self, command, args, channel, **kwargs):
        if command == "fortune":
            return [(1, kwargs["from_nick"], 
            "!{} prints a random, hopefully interesting, adage.".format("fortune"))]
        if command == "all":
            return [(1, kwargs["from_nick"], 
            "Fortune: {ftn}".format(ftn = "fortune"))]

    def fortune(self):
        fortunes = "data/fortunes.txt"
        raw_fort = open(fortunes).read().split("%")
        small_fort = list()
        for f in raw_fort:
            if len(f) <= MAXLINEWIDTH:
                small_f = f.strip().replace("\t","").replace("\n"," ")
                small_fort.append(small_f)
        index = randint(0,len(small_fort)-1)
        return small_fort[index]
