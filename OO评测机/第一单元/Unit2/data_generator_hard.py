import random

ans = ''
minTermNum = 5
maxTermNum = 7
minFactorNum = 3
maxFactorNum = 5
maxSubExprNum = 4
subExprNum = 0
maxBigInteger = 5
BigInteger = 0

def createExpr():
    global ans
    numOfTerms = random.randint(minTermNum, maxTermNum)
    for i in range(numOfTerms):
        addSign()
        addSpace()
        createTerm()
        addSpace()

def createTerm():
    global ans
    numOfFactors = random.randint(minFactorNum, maxFactorNum)
    if getRand():
        ans += '+'
    else:
        ans += '-'
    addSpace()
    createFactor()
    addSpace()
    for i in range(numOfFactors):
        ans += '*'
        addSpace()
        createFactor()
        addSpace()

def createFactor():
    global ans
    global subExprNum
    global maxSubExprNum
    if subExprNum < maxSubExprNum:
        op = random.randint(80,100)
        if 91 <= op <= 100:
            subExprNum += 1
    else:
        op = random.randint(1, 90)
    if 1 <= op <= 45:
        addNum()
    elif 46 <= op <= 90:
        if getRand():
            ans += 'x'
        else:
            ans += 'x'
            addSpace()
            ans += '^'
            addSpace()
            if getRand():
                ans += '+'
            numbit = random.randint(0,1)
            for i in range(numbit):
                ans += str(0)
            ans += str(random.randint(0, 8))
    else:
        ans += '('
        createExpr()
        ans += ')'
        addSpace()
        ans += '^'
        addSpace()
        if getRand():
            ans += '+'
        numbit = random.randint(0, 1)
        for i in range(numbit):
            ans += str(0)
        ans += str(random.randint(0, 8))

def getRand():
    return random.randint(0, 1)

def addSign():
    global ans
    if getRand():
        sign = '+'
    else:
        sign = '-'
    ans += sign

def addSpace():
    global ans
    numOfSpace = random.randint(0, 1)
    for i in range(numOfSpace):
        if getRand():
            sign = ' '
        else:
            sign = '\t'
        ans += sign

def addNum():
    global ans
    global BigInteger
    global maxBigInteger
    addSign()
    if BigInteger < maxBigInteger and getRand():
        numbit = 21
        BigInteger += 1
    else:
        numbit = random.randint(1,3)
    for i in range(numbit):
        ans += str(random.randint(0,9))

createExpr()
print(ans, end = '')