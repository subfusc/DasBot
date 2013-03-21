# -*- coding: utf-8 -*-
# TODO:
# Presedens?
# Koden antar lengde på variabelene, kræsjer hvis mer enn 1
# Støtter ikke unicode
# Operator aritet, kræsjer hvis ikke blir møtt

import math
import re

MAXVARS = 3
SEPERATORSPACES = '   '

class TruthTable(object):

    def __init__(self):
        self.operators = ['+', '&', '>', '~']
        self.maxvars = MAXVARS

    def getOperatorIndex(self, statement):

        index = 0
        bracketSymmetry = 0

        for symbol in statement:
            if symbol in self.operators and bracketSymmetry == 0 and symbol != '~':
                return index
            elif symbol == '(':
                bracketSymmetry += 1
            elif symbol == ')':
                bracketSymmetry -= 1

            index += 1

    def operate(self, operator, varA, varB):

        if operator == '&':
            if varA == '1' and varB == '1':
                return '1'
            return '0'
        if operator == '+':
            if varA == '1' or varB == '1':
                return '1'
            return '0'
        if operator == '>':
            if varA == '1' and varB == '0':
                return '0'
            return '1'

    def makeTree(self, statement):

        operatorIndex = self.getOperatorIndex(statement)

        # If 'entity'
        # Takes care of P or (P) cases
        if operatorIndex == None:
            if len(statement) == 1:
                return statement
            elif statement[0] == '~':
                return ['~', self.makeTree(statement[1:])]
            else:
                return  self.makeTree(statement[1:-1])

        return [statement[operatorIndex], self.makeTree(statement[:operatorIndex]), self.makeTree(statement[operatorIndex+1:])]

    def solveTree(self, tree):
        if len(tree) == 1:
            return tree

        if tree[0] == '~':
            if self.solveTree(tree[1]) == '1':
                return '0'
            else:
                return '1'

        return self.operate(tree[0], self.solveTree(tree[1]), self.solveTree(tree[2]))


class Truth(object):

    def __init__(self):
        self.truth = TruthTable()

    def error(self, message):
        print(message)

    def bracketSymmetry(self, statement):
        sym = 0
        for symbol in statement:
            if symbol == '(':
                sym += 1
            elif symbol == ')':
                sym -= 1

        return sym

    def containsOperator(self, statement):
        for symbol in statement:
            if symbol in self.truth.operators:
                return True
        return False

    def getVariables(self, statement): # TODO: Må identifisere variabler på mer enn et symbol?

        l = re.findall('[a-zA-Z]+', statement)

        variables = { item:[] for item in l }

        if len(variables) > self.truth.maxvars:
            return None

        rows = math.pow(2,len(variables))
        varIndex = 1

        for var in sorted(variables.keys()):
            for i in range(0, 2):
                for j in range(0, int(rows / (varIndex * 2))):
                    variables[var].append(i)
            varIndex += 1

        for var in sorted(variables.keys()):
            while len(variables[var]) != rows:
                variables[var] += variables[var]

        return variables

    def syntaxOk(self, statement):
        legalNext = { '(':'[a-zA-Z~(]',
                      ')':'[\+&>)]',
                      '~':'[a-zA-Z(~]',
                      '+':'[a-zA-Z(~]',
                      '&':'[a-zA-Z(~]',
                      '>':'[a-zA-Z(~]' }

        index = 0
        statementlength = len(statement)

        for symbol in statement:
            if symbol in legalNext:
                if index+1 >= statementlength:
                    return False

                if re.search(legalNext[symbol], statement[index+1]) == None:
                        return False

            index += 1

        return True

    def solve(self, statement):

        tree = self.truth.makeTree(statement)

        return self.truth.solveTree(tree)

    # This starts the process of parsing a logical statement
    # Example statement: "(A + (B & C))"
    def parse(self, originalStatement):

        # Removing spaces making the statement compact, ie "(A+(B&C))"
        statement = originalStatement.replace(" ", "")

        if self.containsOperator(originalStatement) == False:
            self.error("Expression does not contain operators")
            return None
        # Checks for an uneven amount of brackets, ie: "(A + (B & C)))", "(A + B & C))", etc
        if self.bracketSymmetry(statement) != 0:
            self.error("Statement is not symmetrical")
            return None

        # Extracts variables from the statement into a list
        # variables = { 'A', 'B', 'C' ]
        variables = self.getVariables(statement)

        if variables == None:
            self.error("No variables found")
            return None

        if self.syntaxOk(statement) == False:
            self.error("Syntax check failed")
            return None

        # Checks are done
        # Lets work some magic

        # Prepare stuff
        rows = math.pow(2, len(variables))

        output = []
        tmpStr = ""

        # Add truth table header
        for var in sorted(variables.keys()):
            tmpStr += var + SEPERATORSPACES
        tmpStr += '| '
        tmpStr += originalStatement

        output.append(tmpStr)

        resultSpaces = " "

        if originalStatement[-1] == ')':
            operatorIndex = self.truth.getOperatorIndex(originalStatement[1:-1]) + 1
        else:
            operatorIndex = self.truth.getOperatorIndex(originalStatement)

        if operatorIndex == None:
            resultSpaces += ""
            operatorIndex = 0

        for i in range(0, operatorIndex):
            resultSpaces += " "

        # Add each row of variable values and solve statement
        for i in range(0, int(rows)):

            tmpStatement = statement
            tmpStr = ""

            for var in sorted(variables.keys()):
                tmpStr += str(variables[var][i])
                tmpStr += SEPERATORSPACES
                tmpStatement = tmpStatement.replace(var, str(variables[var][i]))
            tmpStr += '|' + resultSpaces

            # solve statement
            tmpStr += str(self.solve(tmpStatement))

            output.append(tmpStr)

        # Return a list of lines for output
        return output

t = Truth()
