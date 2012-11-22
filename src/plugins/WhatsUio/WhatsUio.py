#!/usr/bin/env python 
# -*- coding: utf-8 -*-
import subprocess
import re
import codecs

UIO_USERNAME=''
UIO_SERVERNAME='localhost'
UIO_CSVFILE= 'data/ojd.csv'

class ComputerList(object):

    def __init__(self):
        self.by_computer_name = {}

    def add_computer(self, computer, room):
        computer = computer.lower()
        room = room.lower()
        self.by_computer_name[computer] = room

    def is_computer(self, entity):
        return entity.lower() in self.by_computer_name

    def where_is_computer(self, computer):
        computer = computer.lower()
        return self.by_computer_name[computer] if computer in self.by_computer_name else None

class Room(object):

    def __init__(self, number, room_type):
        self.number = number
        self.room_type = room_type
        self.computers = set()

    def add_computer(self, computer):
        self.computers.add(computer.lower())

    def has_computer(self, computer):
        return computer.lower() in self.computers
        
    def get_computers(self):
        return self.computers

    def get_number(self):
        return self.number
    
class RoomList(object):

    def __init__(self):
        self.by_room_name = {}
        self.by_room_number = {}
        
    def add_room(self, room, number, room_type):
        room = room.lower()
        try:
            number = int(number)
        except ValueError:
            number = number
        
        if not room in self.by_room_name:
            self.by_room_name[room] = Room(number, room_type)
        if type(number) == int and not number in self.by_room_number:
            self.by_room_number[number] = room

    def add_computer(self, room, computer):
        room = room.lower()
        if room in self.by_room_name:
            self.by_room_name[room].add_computer(computer)
            
    def is_room(self, name):
        return name.lower() in self.by_room_name

    def room_location(self, name):
        name = name.lower()
        if name in self.by_room_name:
            return self.by_room_name[name].get_number()
        return None
        
    def room_name(self, number):
        try:
            number = int(number)
            if number in self.by_room_number:
                return self.by_room_number[number]
            return None
        except ValueError:
            return None

    def computer_list(self, room):
        name = room.lower()
        if name in self.by_room_name:
            return self.by_room_name[name].get_computers()
        return None
        
class EntityList(object):

    def __init__(self):
        self.by_name = {}

    def add_entity(self, entity, location, description):
        entity = entity.lower()
        try:
            location = int(location)
        except ValueError: pass

        self.by_name[entity] = (location, description)

    def is_entity(self, entity):
        entity = entity.lower()
        return entity in self.by_name
        
    def locate_entity(self, entity):
        return self.by_name[entity.lower()][0] if entity.lower() in \
          self.by_name else None

    def describe_entity(self, entity):
        entity = entity.lower()
        return self.by_name[entity][1] if entity in self.by_name else None

    def get_entity(self, entity):
        entity = entity.lower()
        return self.by_name[entity] if entity in self.by_name else None

class UserList(object):

    def __init__(self):
        self.are = re.compile("^\S+\s+(ifi-)?(?P<adress>[^-.]+).*")
        if UIO_SERVERNAME != 'localhost':
            self.UIO_LOGIN = ['ssh', UIO_USERNAME + '@' + UIO_SERVERNAME ]
        else:
            self.UIO_LOGIN = []
            
    def is_user(self, username):
        return 0 == subprocess.call(self.UIO_LOGIN + ['id', username])

    def strip_computer_adress(self, line):
        match = self.are.match(line)
        if match:
            return match.group('adress')
        else:
            None
        
    def locate_user(self, username):
        try:
            computers = subprocess.check_output(self.UIO_LOGIN + ['bash', '-c',
                                                                  'rwho|grep ' +
                                                                  username])
            
            computers = set([self.strip_computer_adress(line) for line in computers.split("\n")])
            computers.remove(None)

            return computers
            
        except subprocess.CalledProcessError:
            return None


class WhatsUio(object):
    COMPUTERS = 'maskin'
    ROOMS = ['stue', 'rom', 'ium', 'lab', 'sal']
    
    def __init__(self, file_name):
        self.computers = ComputerList()
        self.rooms = RoomList()
        self.entities = EntityList()
        self.users = UserList()
        self.read_trondth_file(file_name)

    @classmethod
    def ends_with_room(cls, string):
        for room in WhatsUio.ROOMS:
            if string.endswith(room): return True
        return False
        
    def where_is_user(self, username):
        computer = self.users.locate_user(username)
        if computer:
            for comp in computer:
                if self.computers.is_computer(comp):
                    return self.computers.where_is_computer(comp)
        return None
            
    def read_trondth_file(self, name):
        f = codecs.open(name, encoding='utf-8')
        for line in f:
            print(line),
            line = line.rstrip()
            line = line.split(';')
            if line[2] == WhatsUio.COMPUTERS:
                self.computers.add_computer(line[0], line[1])
                self.rooms.add_computer(line[1], line[0])
            elif WhatsUio.ends_with_room(line[2]):
                self.rooms.add_room(line[0], line[1], line[2])
            else:
                self.entities.add_entity(line[0], line[1], line[2])
        print self.rooms
