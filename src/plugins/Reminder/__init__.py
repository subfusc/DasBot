# -*- coding: utf-8 -*-
# Basic interface class for communicating with an IRC server.
# Copyright (C) 2012  Sindre Wetjen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import time

class Plugin(object):

    def __init__(self):
        self.job = None
    
    def _print_reminder(self, channel, user, ti, msg):
        self.job = None
        return [(0, channel, user, msg), 
                (0, channel, user, "Real time used: {t}".format(t = (time.time() - ti)))]
    
    def cmd(self, command, args, channel, **kwargs):
        if command == "reminder":
            args = args.split()
            if len(args) >= 2 and self.job == None:
               self.job = kwargs['new_job']((time.time() + int(args[0]),
                                             self._print_reminder,
                                             [channel,
                                              kwargs['from_nick'],
                                              time.time(),
                                              " ".join(args[1:])]))
               return [(0, channel,
                        kwargs['from_nick'],
                        "Okay, I will remind you of that in {s} seconds.".format(s = args[0]))]
           
        if command == "stopreminder":
            if self.job:
                kwargs['del_job'](self.job)
                self.job = None
                return [(0, channel, kwargs['from_nick'], "Done!")]
                
