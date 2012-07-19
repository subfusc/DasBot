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
from GlobalConfig import *
from PluginBot import PluginBot
import threading
import time
import os

class CronTab(object):

    def __init__(self):
        self.__tab = []
        self.__lock = threading.Lock()

    def __len__(self):
        self.__lock.acquire()
        length = len(self.__tab)
        self.__lock.release()
        return length

    def add_job(self, job):
        self.__lock.acquire()
        for x, l_job in enumerate(self.__tab):
            if job[0] > l_job[0]:
                self.__tab.insert(x, job)
                break
        else:
            self.__tab.append(job)
        self.__lock.release()
        
    def peek_job(self):
        self.__lock.acquire()
        job = self.__tab[-1]
        self.__lock.release()
        return job
        
    def pop_job(self):
        self.__lock.acquire()
        if VERBOSE: print("CRONTAB: " + str(self.__tab))
        job = self.__tab.pop()
        self.__lock.release()
        return job
        
class CronJob(threading.Thread):

    def __init__(self, send_function):
        super(CronJob, self).__init__()
        self.crontab = CronTab()
        self.lock = threading.Lock()
        self.timer = None
        self.exit = False
        self.lock_lock = threading.Lock()
        self.send_function = send_function

    def stop(self):
        if VERBOSE: print("DELETING CRONJOB")
        self.exit = True
        if self.timer:
            self.timer.cancel()
        self.__release_main_lock()
        
    def new_job(self, job):
        self.crontab.add_job(job)
        self.__release_main_lock()

    def __aquire_both_locks(self):
        if DEBUG: print("Aquire both locks")
        self.lock_lock.acquire()
        self.lock.acquire()

    def __release_lock_lock_and_wait(self):
        if DEBUG: print("release lock lock and wait")
        self.lock_lock.release()
        self.lock.acquire()

    def __release_main_lock(self):
        if DEBUG: print("release main lock")
        self.lock_lock.acquire()
        if self.lock.locked():
            self.lock.release()
        self.lock_lock.release()
        
    def run(self):
        print("Starting CronJob Daemon")
        while not self.exit:
            print("==::LOOP::==")
            self.__aquire_both_locks()
            if len(self.crontab) > 0:
                self.timer = threading.Timer(self.crontab.peek_job()[0] - time.time(), 
                                             CronJob.__release_main_lock, [self])
                self.timer.start()
                self.__release_lock_lock_and_wait()
                self.__release_main_lock()
                if self.crontab.peek_job()[0] < time.time():
                    try:
                        t = self.crontab.pop_job()
                        self.send_function(t[1](*t[2]))
                    except Exception as e:
                        print("Error in The CronTab List: {ex}".format(ex = e))
            else:
                self.__release_lock_lock_and_wait()
                self.__release_main_lock()
        if DEBUG: print("Exited Safely")

class CronBot(PluginBot):

    def __init__(self):
        super(CronBot, self).__init__()
        self.cronjob = CronJob(self._send_message)
        if START_CRON_BOT:
            self.cronjob.start()
        
    def __del__(self):
        super(CronBot, self).__del__()
        if START_CRON_BOT:
            self.cronjob.stop()

    def stop(self):
        super(CronBot, self).stop()
        if START_CRON_BOT:
            self.cronjob.stop()
        
    def cmd(self, command, args, channel, **kwargs):
        if kwargs['auth_level'] > 95:
            if command == 'reloadcron' or command == 'rlcron':
                self.cronjob.stop()
                self.cronjob = CronJob(self._send_message)
                self.cronjob.start()
        kwargs['new_job'] = self.cronjob.new_job
        super(CronBot, self).cmd(command, args, channel, **kwargs)
