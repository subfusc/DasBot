# -*- coding: utf-8 -*-
import math

VARLIMIT = 3


class Plugin(object):

    def __init__(self):
        pass

    def help(self, command, argc, channel, **kwargs):
        if command == 'tt':
            return [(1, kwargs['from_nick'], "!tt <logic formula>"),
                    (1, kwargs['from_nick'], "Gives you a truth table for the formula you entered."),
                    (1, kwargs['from_nick'], "Syntax:"),
                    (1, kwargs['from_nick'], "    &     : Logical AND"),
                    (1, kwargs['from_nick'], "    +     : Logical OR"),
                    (1, kwargs['from_nick'], "    >     : Implication"),
                    (1, kwargs['from_nick'], "    ~     : Negation"),
                    (1, kwargs['from_nick'], "    a-zA-Z: Variables (3 variable limit)")]

    def cmd(self, command, args, channel, **kwargs):

        if command == 'tt':
            vars = self.getVariables(args) 
            if len(vars) <= VARLIMIT:
                return self.getTable(vars, args, channel) # change to kwargs['from_nick']
        if command == 'ttest':
            variables = self.getVariables(args)
            variables = variables.keys()
            variables.sort()
            return [(0, channel, str(variables))]

    def getVariables(self, args):
        charc = {}
        for char in args:
            if char.isalpha():
                if char not in charc:
                    charc[char] = 1
                else:
                    charc[char] += 1
        return charc

    def getTable(self, vars, args, user):

        vars = vars.keys()
        vars.sort()

        table = [ ] 
        
        line = ""
        for variable in vars:
            line += "    " + variable

        line += " | F = " + args

        table.append( (0, user, line) )
        line = ""

        numberOfLines = pow(2, len(vars)) # 4
        
        totalValues = [ ]

        for varNumber in range(1, len(vars)+1):
            varValue = [ ]
            
            for ones in range(0, (numberOfLines / 2) / varNumber):
                varValue.append(1)
            for zeroes in range(0, (numberOfLines / 2) / varNumber):
                varValue.append(0)

#while len(varValue) != numberOfLines:
                varValue.append( varValue )
            
            totalValues.append(varValue)

        return [(0, user, repr(totalValues))]

        for lineNumber in range(0, numberOfLines):
            line = ""
            for varNumber in range(0, len(vars)):
                line += "    " + str(totalValues[varNumber][lineNumber])
            table.append( (0, user, line) )

        table.append( (0, user, str(totalValues)) )

        return table
