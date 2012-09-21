import truth

tt = truth.Truth()
formula = None
values = None

def test(test, expectedValue):

    actualValue = tt.parseAndSolve(values, formula)

    if actualValue != None:
        if expectedValue == actualValue:
            print("Test {}: passed".format(test))

        else:
            print("Test {}: failed".format(test))

def basicOperatorTesting():
    andf = "A & B"
    orf = "A + B"
    impf = "A > B"

    global formula
    global values

    print("\nTesting A = 0, B = 0\n")

    values = { 'A':'0', 'B':'0' }

    formula = andf
    test("&", '0')
    formula = orf
    test("+", '0')
    formula = impf
    test(">", '1')

    print("\nTesting A = 1, B = 0\n")

    values = { 'A':'1', 'B':'0' }

    formula = andf
    test("&", '0')
    formula = orf
    test("+", '1')
    formula = impf
    test(">", '0')

    print("\nTesting A = 0, B = 1\n")

    values = { 'A':'0', 'B':'1' }

    formula = andf
    test("&", '0')
    formula = orf
    test("+", '1')
    formula = impf
    test(">", '1')

    print("\nTesting A = 1, B = 1\n")

    values = { 'A':'1', 'B':'1' }

    formula = andf
    test("&", '1')
    formula = orf
    test("+", '1')
    formula = impf
    test(">", '1')

def doBasicParanthesis():



# Do tests
#basicOperatorTesting()
