from tt import TruthTable, Truth

LEVEL = 1

class Test:

    def __init__(self, level):
        self.t = TruthTable()
        self.truth = Truth()
        self.level = level

    def OR(self):
        if self.level == 0:
            return [['+', 'A', 'B'], "A+B", 1, "1+1"]
        elif self.level == 1:
            return [['+', 'A', ['+', 'B', 'C']] , "A+(B+C)", 1, "0+(1+0)"]

    def AND(self):
        if self.level == 0:
            return [['&', 'A', 'B'] , "A&B", 1, "1&1"]
        if self.level == 1:
            return [['&', 'A', ['&', 'B', 'C']], "A&(B&C)", 0, "0&(1&1)"]

    def IMPL(self):
        if self.level == 0:
            return [['>', 'A', 'B'] , "A>B", 0, "1>0"]
        if self.level == 1:
            return [['>', 'A', ['>', 'B', 'C']] , "A>(B>C)", 0, "1>(1>0)"]

    def NOT(self):
        if self.level == 0:
            return [['+', ['~', 'A'], 'B'], "~A+B", 0, "~0+0"]
        if self.level == 1:
            return [['>', 'A', ['~', ['>', 'B', 'C']]], "A>~(B>C)", 0, "1>~(0>1)"]

    def test(self, expected, actual):
        print("Testing: " + str(expected) + " |vs| " + str(actual))
        if expected == actual:
            print("    Success!")
        else:
            print("    Failed")
        print()

    def testMakeTree(self):
        print("Test: makeTree")
        print("Test level: " + str(self.level))
        print("#############")
        print("#############")

        print("Testing OR:")
        # Get testdata
        td = self.OR()
        self.test(td[0],self.t.makeTree(td[1]))

        print("Testing AND:")
        td = self.AND()
        self.test(td[0],self.t.makeTree(td[1]))

        print("Testing IMPL:")
        td = self.IMPL()
        self.test(td[0],self.t.makeTree(td[1]))

        print("Testing NOT:")
        td = self.NOT()
        self.test(td[0], self.t.makeTree(td[1]))

        print("############")
        print("############")
        print("Testing finished.")

    def testSolveTree(self):
        print("Test: solveTree")
        print("Test level: " + str(self.level))
        print("#############")
        print("#############")

        # Get testdata
        td = self.OR()
        self.test(td[2],self.t.solveTree(self.t.makeTree(td[3])))

        print("Testing AND:")
        td = self.AND()
        self.test(td[2],self.t.solveTree(self.t.makeTree(td[3])))

        print("Testing IMPL:")
        td = self.IMPL()
        self.test(td[2],self.t.solveTree(self.t.makeTree(td[3])))

        print("Testing NOT:")
        td = self.NOT()
        self.test(td[2],self.t.solveTree(self.t.makeTree(td[3])))

        print("############")
        print("############")

    def testParser(self):
        pass

t = Test(LEVEL)
t.testSolveTree()
