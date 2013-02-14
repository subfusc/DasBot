# -*- coding: utf-8 -*-
from WhatsUio import WhatsUio, UIO_CSVFILE

class Plugin(object):

    def __init__(self): 
        self.db = WhatsUio(UIO_CSVFILE)

    @classmethod
    def number_to_reply(cls, number):
        if type(number) == int:
            location = number % 100 
            side = (number / 100) % 10 
            etg = (number / 1000)

            if location >= 40:
                if etg <= 2:
                    location = "under tårnet"
                else:
                    location = "i tårnet"
            else:
                location = "ikke i tårnet"
                
            return "{e} etg. {l}, på den siden som er {s}.".format(e = etg, s = "mot bekken" if side > 2 else "mot gamle ifi", l = location)
        else:
            return number

    def make_response(self, arg, channel, **kwargs):
        if arg in kwargs['nick_to_user']: arg = kwargs['nick_to_user'][arg]
        if arg == 'jeg':
            room = self.db.where_is_user(kwargs['from_nick'])
            if room:
                return [(0, channel, kwargs['from_nick'], "Du er på {r}".format(r = room))] 
            else:
                return [(0, channel, kwargs['from_nick'], "Du er ikke pålogget på ifi.")]
        if self.db.users.is_user(arg):
            room = self.db.where_is_user(arg)
            if room:
                return [(0, channel, kwargs['from_nick'], "{u} er på {r}".format(r = room, u = arg.encode('utf-8')))] 
            else:
                return [(0, channel, kwargs['from_nick'], "{u} er ikke pålogget på ifi.".format(u = arg.encode('utf-8')))]
        elif self.db.computers.is_computer(arg): 
            return [(0, channel, kwargs['from_nick'], "{m} er i {r}".format(m = arg.encode('utf-8'), r = self.db.computers.where_is_computer(arg)))] 
        elif self.db.rooms.is_room(arg):
            return [(0, channel, kwargs['from_nick'], "{r} ({n}) er i {b}".format(r = arg.encode('utf-8'), n = self.db.rooms.room_location(arg),
                                                                            b = Plugin.number_to_reply(self.db.rooms.room_location(arg))))]
        elif self.db.entities.is_entity(arg):
            return [(0, channel, kwargs['from_nick'], "{e} er i {b}".format(e = arg.encode('utf-8'), b = self.db.entities.locate_entity(arg)))]
        
    def cmd(self, cmd, args, channel, **kwargs):
        if cmd == 'hvorer' and args != None and kwargs['auth_nick'] != None:
            try:
                args = args.decode('utf-8')
                arg_list = args.split()
                return self.make_response(arg_list[0], channel, **kwargs)
            except Exception as e:
                print("I got an exception in WhatsUio, probably encoding error")
                print e

    def listen(self, line, channel, **kwargs):
        if kwargs['auth_nick'] != None:
            try:
                line = line.decode('utf-8')
                line = line.replace('?', '')
                line = line.replace('!', '')
                line = line.replace('.', '')
                line = line.replace(',', '')
                line = line.split()
                if "Hvor" in line or 'hvor' in line:
                    er = 0
                    hvor = 0
                    for i, word in enumerate(line):
                        if word == "hvor" or word == "Hvor":
                            hvor = i
                        elif word == "er":
                            er = i

                    arg = None
                    if (er - hvor) == 1 and (er + 1) < len(line):
                        arg = line[er + 1]
                    elif (hvor + 1) < len(line) and er != 0:
                        arg = line[hvor + 1]
                    # print("LINE: {l} :: ARG: {a} :: HVOR: {h} :: ER: {e}".format(l = line, a = arg.encode('utf-8'), h = hvor, e = er))
                    if arg:
                        return self.make_response(arg, channel, **kwargs)
        
            except Exception as e:
                print("got an error in WhatsUio, probably an encoding error")
                print(e)
