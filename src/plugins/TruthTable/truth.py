# --*-- coding: utf-8 --*--

class Truth(object):

    def __init__(self):
        pass

    # A & B
    def parseAndSolve(self, values, expression):
        formula = expression.replace(" ", "")

        for key in values.keys():
            formula = formula.replace(key, values[key])

        return self.solve(formula)

    def solve(self, formula):

        result = [ ]

        index = 0
        while index < len(formula):
            if formula[index] != '(':
                result.append(formula[index])
            else:
                start = index + 1
                
                while formula[index] != ')':
                    index += 1
                
                result.append( self.solve(formula[start:index]) )
            
            index += 1

        return self.parseResult(result)



    def parseResult(self, result):
        if len(result) > 1:

            var1 = None
            var2 = None
            operator = None
            
            for element in result:
                if self.isOperator(element) == '1':
                    operator = element
                else:
                    if not var1:
                        var1 = element
                    else:
                        var2 = element

                if var1 and var2 and operator:
                    var1 = self.calc(operator, var1, var2)
                    var2 = None
                    operator = None

            return var1

        else:
            return result[0]

    def calc(self, operator, var1, var2):
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
        elif operator == '~':
            if var1 == '1':
                return '0'
            else:
                return '1'

    def isOperator(self, c):
        if c == '&':
            return '1'
        elif c == '+':
            return '1'
        elif c == '>':
            return '1'
        elif c == '~':
            return '1'

        return '0'
