# -*- coding: utf-8 -*-
# Classes to make a cron system for an IRC bot.
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
import GlobalConfig as conf
from AdminBot import AdminBot
import threading
import time
import os
import sys
from math import ceil

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
        same = 0
        timestamp = job[0]
        function = job[1]
        args = job[2]
        
        for x, l_job in enumerate(self.__tab):
            if timestamp == l_job[0]: same += 1
            if timestamp > l_job[0]:
                self.__tab.insert(x, (timestamp, function, args))
                rval = (same, timestamp)
                break
        else:
            self.__tab.append((timestamp, function, args))
            rval = (0, timestamp)
        self.__lock.release()
        return rval
        
    def del_job(self, job_id):
        self.__lock.acquire()
        # sys.stderr.write("DELETING\n")
        if not (len(job_id) != 2 or type(job_id[1]) != float or time.time() > job_id[1]):
            same = job_id[0]
            timestamp = job_id[1]
            for x, l_job in enumerate(self.__tab):
                if timestamp == l_job[0]:
                    if same == 0:
                        # sys.stderr.write("DELETING: " + str(self.__tab[x]) + " :: " + str(timestamp) + "\n")
                        del(self.__tab[x])
                        break
                    else: same -= 1
        #sys.stderr.write(str(self.__tab) + "\n")
        self.__lock.release()

    def get_next_job(self, t):
        self.__lock.acquire()
        rval = None
        if len(self.__tab) > 0:
            rval = self.__tab.pop() if t > self.__tab[-1][0] else self.__tab[-1]
        self.__lock.release()
        return rval
        
    def peek_job(self):
        self.__lock.acquire()
        job = self.__tab[-1]
        self.__lock.release()
        return job
        
    def pop_job(self):
        self.__lock.acquire()
        if conf.VERBOSE: print("CRONTAB: " + str(self.__tab))
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
        if conf.VERBOSE: print("DELETING CRONJOB")
        self.exit = True
        if self.timer:
            self.timer.cancel()
        self.__release_main_lock()
        
    def new_job(self, job):
        rval = self.crontab.add_job(job)
        # sys.stderr.write(str(len(self.crontab))+ "\n")
        self.__release_main_lock()
        return rval

    def del_job(self, job_id):
        """
        Delete a job from the cron tab. The id looks like this = (number, timestamp) and is returned
        from new_job
        """
        self.crontab.del_job(job_id)
         
    def __aquire_both_locks(self):
        if conf.DEBUG: print("Aquire both locks")
        self.lock_lock.acquire()
        # sys.stderr.write("SECOND LOCK\n")
        self.lock.acquire()
        # sys.stderr.write("OUT!\n")

    def __release_lock_lock_and_wait(self):
        if conf.DEBUG: print("release lock lock and wait")
        self.lock_lock.release()
        self.lock.acquire()

    def __release_main_lock(self):
        if conf.DEBUG: print("release main lock")
        self.lock_lock.acquire()
        if self.lock.locked():
            self.lock.release()
        self.lock_lock.release()
        
    def run(self):
        print("Starting CronJob Daemon")
        while not self.exit:
            if conf.DEBUG: print("==::LOOP::==")
            self.__aquire_both_locks()
            #sys.stderr.write(str(len(self.crontab)) + "\n")
            if len(self.crontab) > 0:
                # sys.stderr.write(str(self.crontab.peek_job()) + "\n")
                self.timer = threading.Timer(self.crontab.peek_job()[0] - time.time(), 
                                             CronJob.__release_main_lock, [self])
                self.timer.start()
                self.__release_lock_lock_and_wait()
                self.__release_main_lock()
                t = time.time()
                job = self.crontab.get_next_job(t)
                if job and job[0] < t:
                    try:
                        self.send_function(job[1](*job[2]))
                    except Exception as e:
                        print("Error in The CronTab List: {ex}".format(ex = e))
            else:
                self.__release_lock_lock_and_wait()
                self.__release_main_lock()
        if conf.DEBUG: print("Exited Safely")

class CronBot(AdminBot):

    def __init__(self):
        super(CronBot, self).__init__()
        self.cronjob = CronJob(self._send_message)
        if conf.START_CRON_BOT:
            self.cronjob.start()
        
    def stop(self):
        super(CronBot, self).stop()
        if conf.START_CRON_BOT:
            self.cronjob.stop()
        
    def cmd(self, command, args, channel, **kwargs):
        if kwargs['auth_level'] > 95:
            if command == 'reloadcron' or command == 'rlcron':
                self.cronjob.stop()
                self.cronjob = CronJob(self._send_message)
                self.cronjob.start()
        kwargs['new_job'] = self.cronjob.new_job
        kwargs['del_job'] = self.cronjob.del_job
        super(CronBot, self).cmd(command, args, channel, **kwargs)

    def help(self, command, args, channel, **kwargs):
        if command == 'reloadcron':
            self.notify(kwargs['from_nick'], '!reloadcron - Forcfully reload the crontab if there was an error')
        elif command == 'all':
            self.notify(kwargs['from_nick'], 'CronBot: reloadcron')
        super(CronBot, self).help(command, args, channel, **kwargs)


# def local_print(*args):
#    sys.stderr.write(str(args) + "\n")
#    return args

# if __name__ == '__main__':
#     c = CronJob(local_print)
#     c.start()
#     time.sleep(2)
#     c.new_job((time.time() + 10, local_print, ["10"]))
#     c.new_job((time.time() + 30, local_print, ["30"]))
#     job1 = c.new_job((time.time() + 15, local_print, ["15"]))
#     job2 = c.new_job((time.time() + 5, local_print, ["5"]))
#     c.new_job((time.time() + 10, local_print, ["10 - 2"]))
#     time.sleep(10)
#     c.del_job(job2)
#     c.del_job(job1)
#     while len(c.crontab) > 0:
#         time.sleep(2)
#     c.stop()
#
