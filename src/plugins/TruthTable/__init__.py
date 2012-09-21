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

        pcount = 0

        for char in args:
            if pcount < 0:
                return[(0, user, "Error. Check your paranthesises")]
            if char == '(': pcount += 1
            if char == ')': pcount -= 1

        if pcount != 0:
            return [(0, user, "Error. Check your paranthesises")]

        vars = vars.keys()
        vars.sort()

        table = [ ] 
        
        line = ""
        for variable in vars:
            line += "    " + str(variable)

        line += " | F = " + str(args)

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

            while len(varValue) != numberOfLines:
                varValue += varValue
            
            totalValues.append(varValue)

        for lineNumber in range(0, numberOfLines):

            line = ""

            for varNumber in range(0, len(vars)):
                line += "    " + str(totalValues[varNumber][lineNumber])

            result = 0

            result = self.parseFormula(vars,line,args) 

            line += " | " + str(result)

            table.append( (0, user, line) )

            
#return [(0,user, str(self.parseFormula(vars, "    1    1    1", args)))]
        return table

    def parseFormula(self, vars, line, args):
        
        values = line.replace(" ", "")  
        formula = args.replace(" ", "")

        i = 0
        varWithValue = { }

        for var in vars:
            varWithValue[var] = values[i]
            i += 1

        # {A:1, B:2, C:3} 
        # (A+(B&C))

        for var in varWithValue.keys():
            formula = formula.replace(str(var), str(varWithValue[var]))
        
        return self.solve(formula)

    def solve(self, expression):

        result = [ ]
        index = 0

        while index < len(expression):
            
            current = expression[index]
            
            if current != '(':
                result.append(current)
                index += 1
            else:  
                start = index + 1
                end = self.getNextParanthesisEnd(expression, index) # - 1 ? 
                result.append(self.solve(expression[start:end]))
                index = end + 1


        if(len(result) > 1):
            print "result: " + str(result)
            var1 = None
            var2 = None
            operator = None
            for element in result:
                if var1 and var2 and operator:
                    var1 = self.calculate(operator, var1, var2)
                    var2 = None
                    operator = None

                if not self.isOperator(element):
                    if not var1:
                        var1 = element
                    elif not var2:
                        var2 = element
                else:
                    operator = element

            if var1 and var2 and operator:
                var1 = self.calculate(operator, var1, var2)
            print "returns: " + str(var1)
            return var1

        return result[0]

                    
    def getNextParanthesisEnd(self, expression, index):
        while index < len(expression):
            if expression[index] == ')':
                return index
            else:
                if index:
                    index += 1

    def calculate(self, operator, var1, var2):
        if operator == '&':
            if var1 == '1' and var2 == '1':
                return '1'
            else:
                return '0'
        elif operator == '+':
            if var1 == '1' or var2 == '1':
                return '1'
            else:
                return '0'
        elif operator == '>':
            if not (var1 == '1' and var2 == '0'):
                return '1'
            else:
                return '0'

    def isOperator(self, char):
        
        if(char == '&'):
            return 1
        elif(char == '+'):
            return 1
        elif(char == '>'):
            return 1
        elif(char == '~'):
            return 1

        return 0
